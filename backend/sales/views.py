from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Sum
from .models import Lead, Customer, Deal, DealActivity
from .serializers import (
    LeadSerializer,
    CustomerSerializer,
    DealSerializer,
    DealActivitySerializer
)
from users.permissions import CanAccessLeads, CanAccessCustomers, IsSalesTeam


class LeadViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing leads
    """
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated, CanAccessLeads]

    def get_queryset(self):
        """
        Filter leads based on query parameters and user permissions
        """
        queryset = Lead.objects.select_related('assigned_to').all()

        # Non-admins only see their own leads or unassigned leads
        if self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(
                Q(assigned_to=self.request.user) | Q(assigned_to__isnull=True)
            )

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by assigned user
        assigned_to = self.request.query_params.get('assigned_to', None)
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)

        # Filter by source
        source = self.request.query_params.get('source', None)
        if source:
            queryset = queryset.filter(source=source)

        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(restaurant_name__icontains=search) |
                Q(contact_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Auto-assign to current user if sales rep"""
        if self.request.user.department == 'sales' and not serializer.validated_data.get('assigned_to'):
            serializer.save(assigned_to=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def mark_contacted(self, request, pk=None):
        """Mark lead as contacted"""
        lead = self.get_object()
        lead.status = Lead.Status.CONTACTED
        if not lead.first_contacted_at:
            lead.first_contacted_at = timezone.now()
        lead.save()
        return Response(self.get_serializer(lead).data)

    @action(detail=True, methods=['post'])
    def qualify(self, request, pk=None):
        """Mark lead as qualified"""
        lead = self.get_object()
        lead.status = Lead.Status.QUALIFIED
        lead.save()
        return Response(self.get_serializer(lead).data)

    @action(detail=True, methods=['post'])
    def disqualify(self, request, pk=None):
        """Mark lead as disqualified"""
        lead = self.get_object()
        lead.status = Lead.Status.DISQUALIFIED
        lead.save()
        return Response(self.get_serializer(lead).data)

    @action(detail=False, methods=['get'])
    def my_leads(self, request):
        """Get leads assigned to current user"""
        queryset = self.get_queryset().filter(assigned_to=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get lead statistics"""
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'new': queryset.filter(status=Lead.Status.NEW).count(),
            'contacted': queryset.filter(status=Lead.Status.CONTACTED).count(),
            'qualified': queryset.filter(status=Lead.Status.QUALIFIED).count(),
            'disqualified': queryset.filter(status=Lead.Status.DISQUALIFIED).count(),
            'converted': queryset.filter(status=Lead.Status.CONVERTED).count(),
        }

        # By source
        by_source = list(queryset.values('source').annotate(count=Count('id')))
        stats['by_source'] = by_source

        return Response(stats)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing customers
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, CanAccessCustomers]

    def get_queryset(self):
        """Filter customers based on query parameters and permissions"""
        queryset = Customer.objects.select_related('sales_rep', 'cs_rep').all()

        # Sales reps see only their customers (unless admin/manager)
        if self.request.user.department == 'sales' and self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(sales_rep=self.request.user)

        # CS reps see only their customers (unless admin/manager)
        if self.request.user.department == 'customer_success' and self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(cs_rep=self.request.user)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by health score
        health_min = self.request.query_params.get('health_min', None)
        if health_min:
            queryset = queryset.filter(health_score__gte=health_min)

        health_max = self.request.query_params.get('health_max', None)
        if health_max:
            queryset = queryset.filter(health_score__lte=health_max)

        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(restaurant_name__icontains=search) |
                Q(contact_name__icontains=search) |
                Q(phone__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['get'])
    def my_customers(self, request):
        """Get customers assigned to current user"""
        if request.user.department == 'sales':
            queryset = self.get_queryset().filter(sales_rep=request.user)
        elif request.user.department == 'customer_success':
            queryset = self.get_queryset().filter(cs_rep=request.user)
        else:
            queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def at_risk(self, request):
        """Get at-risk customers (health score < 50)"""
        queryset = self.get_queryset().filter(health_score__lt=50)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get customer statistics"""
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'onboarding': queryset.filter(status=Customer.Status.ONBOARDING).count(),
            'active': queryset.filter(status=Customer.Status.ACTIVE).count(),
            'at_risk': queryset.filter(status=Customer.Status.AT_RISK).count(),
            'churned': queryset.filter(status=Customer.Status.CHURNED).count(),
            'health_critical': queryset.filter(health_score__lt=50).count(),
            'health_at_risk': queryset.filter(health_score__gte=50, health_score__lt=70).count(),
            'health_good': queryset.filter(health_score__gte=70).count(),
        }

        return Response(stats)


class DealViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing deals
    """
    queryset = Deal.objects.all()
    serializer_class = DealSerializer
    permission_classes = [IsAuthenticated, IsSalesTeam]

    def get_queryset(self):
        """Filter deals based on query parameters and permissions"""
        queryset = Deal.objects.select_related(
            'customer',
            'sales_rep',
            'lead'
        ).prefetch_related('activities').all()

        # Non-admins only see their own deals
        if self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(sales_rep=self.request.user)

        # Filter by stage
        stage = self.request.query_params.get('stage', None)
        if stage:
            queryset = queryset.filter(stage=stage)

        # Filter by sales rep
        sales_rep = self.request.query_params.get('sales_rep', None)
        if sales_rep:
            queryset = queryset.filter(sales_rep_id=sales_rep)

        # Exclude closed deals by default
        exclude_closed = self.request.query_params.get('exclude_closed', 'true')
        if exclude_closed.lower() == 'true':
            queryset = queryset.exclude(
                stage__in=[Deal.Stage.CLOSED_WON, Deal.Stage.CLOSED_LOST]
            )

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Auto-assign to current user if not specified"""
        if not serializer.validated_data.get('sales_rep'):
            serializer.save(sales_rep=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def move_stage(self, request, pk=None):
        """Move deal to a different stage"""
        deal = self.get_object()
        new_stage = request.data.get('stage')

        if new_stage not in dict(Deal.Stage.choices):
            return Response(
                {'error': 'Invalid stage'},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_stage = deal.stage
        deal.stage = new_stage

        # Update probability based on stage
        stage_probabilities = {
            Deal.Stage.NEW_LEAD: 10,
            Deal.Stage.CONTACT_MADE: 20,
            Deal.Stage.QUALIFIED: 30,
            Deal.Stage.DEMO_SCHEDULED: 40,
            Deal.Stage.DEMO_COMPLETED: 50,
            Deal.Stage.PROPOSAL_SENT: 60,
            Deal.Stage.NEGOTIATION: 75,
            Deal.Stage.CONTRACT_SENT: 90,
            Deal.Stage.CLOSED_WON: 100,
            Deal.Stage.CLOSED_LOST: 0,
        }
        deal.probability = stage_probabilities.get(new_stage, deal.probability)

        # If closed won, set close date
        if new_stage == Deal.Stage.CLOSED_WON and not deal.actual_close_date:
            deal.actual_close_date = timezone.now().date()

        deal.save()

        # Log activity
        DealActivity.objects.create(
            deal=deal,
            user=request.user,
            activity_type=DealActivity.ActivityType.NOTE,
            notes=f"Deal moved from {dict(Deal.Stage.choices)[old_stage]} to {deal.get_stage_display()}"
        )

        return Response(self.get_serializer(deal).data)

    @action(detail=True, methods=['post'])
    def add_activity(self, request, pk=None):
        """Add activity to deal"""
        deal = self.get_object()
        serializer = DealActivitySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(deal=deal, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def my_deals(self, request):
        """Get deals assigned to current user"""
        queryset = self.get_queryset().filter(sales_rep=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pipeline_summary(self, request):
        """Get summary of deals by stage"""
        queryset = self.get_queryset().exclude(
            stage__in=[Deal.Stage.CLOSED_WON, Deal.Stage.CLOSED_LOST]
        )

        summary = queryset.values('stage').annotate(
            count=Count('id'),
            total_value=Sum('value')
        ).order_by('stage')

        # Calculate total pipeline value
        total_value = sum(item['total_value'] or 0 for item in summary)
        total_count = sum(item['count'] for item in summary)

        return Response({
            'by_stage': list(summary),
            'total_value': total_value,
            'total_count': total_count
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get deal statistics"""
        queryset = self.get_queryset()

        # Calculate stats for current month
        from datetime import datetime
        current_month_start = datetime.now().replace(day=1)

        stats = {
            'total_open': queryset.exclude(stage__in=[Deal.Stage.CLOSED_WON, Deal.Stage.CLOSED_LOST]).count(),
            'closed_won_this_month': queryset.filter(
                stage=Deal.Stage.CLOSED_WON,
                actual_close_date__gte=current_month_start
            ).count(),
            'closed_lost_this_month': queryset.filter(
                stage=Deal.Stage.CLOSED_LOST,
                updated_at__gte=current_month_start
            ).count(),
            'total_pipeline_value': queryset.exclude(
                stage__in=[Deal.Stage.CLOSED_WON, Deal.Stage.CLOSED_LOST]
            ).aggregate(total=Sum('value'))['total'] or 0,
            'won_value_this_month': queryset.filter(
                stage=Deal.Stage.CLOSED_WON,
                actual_close_date__gte=current_month_start
            ).aggregate(total=Sum('value'))['total'] or 0,
        }

        # Calculate win rate
        total_closed = stats['closed_won_this_month'] + stats['closed_lost_this_month']
        if total_closed > 0:
            stats['win_rate'] = round((stats['closed_won_this_month'] / total_closed) * 100, 1)
        else:
            stats['win_rate'] = 0

        return Response(stats)


class DealActivityViewSet(viewsets.ModelViewSet):
    """
    API endpoints for deal activities
    """
    queryset = DealActivity.objects.all()
    serializer_class = DealActivitySerializer
    permission_classes = [IsAuthenticated, IsSalesTeam]

    def get_queryset(self):
        """Filter activities by deal and user permissions"""
        queryset = DealActivity.objects.select_related('deal', 'user').all()

        # Non-admins only see activities on their own deals
        if self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(deal__sales_rep=self.request.user)

        # Filter by deal
        deal_id = self.request.query_params.get('deal', None)
        if deal_id:
            queryset = queryset.filter(deal_id=deal_id)

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        """Automatically set user when creating activity"""
        serializer.save(user=self.request.user)
