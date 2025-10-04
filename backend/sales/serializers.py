from rest_framework import serializers
from .models import Deal, DealActivity
from users.models import User
from marketing.models import Lead
from core.models import Customer

class UserSerializer(serializers.ModelSerializer):
    """Simple user serializer for nested data"""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'department']


class LeadSerializer(serializers.ModelSerializer):
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)

    class Meta:
        model = Lead
        fields = [
            'id',
            'restaurant_name',
            'contact_name',
            'phone',
            'email',
            'location',
            'instagram',
            'status',
            'source',
            'campaign_id',
            'score',
            'assigned_to',
            'assigned_to_detail',
            'first_contact_due',
            'first_contacted_at',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'first_contact_due']


class CustomerSerializer(serializers.ModelSerializer):
    sales_rep_detail = UserSerializer(source='sales_rep', read_only=True)
    cs_rep_detail = UserSerializer(source='cs_rep', read_only=True)

    class Meta:
        model = Customer
        fields = [
            'id',
            'restaurant_name',
            'contact_name',
            'phone',
            'email',
            'location',
            'address',
            'instagram',
            'number_of_locations',
            'cuisine_type',
            'status',
            'health_score',
            'sales_rep',
            'sales_rep_detail',
            'cs_rep',
            'cs_rep_detail',
            'stripe_customer_id',
            'activated_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DealActivitySerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)

    class Meta:
        model = DealActivity
        fields = [
            'id',
            'deal',
            'user',
            'user_detail',
            'activity_type',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class DealSerializer(serializers.ModelSerializer):
    customer_detail = CustomerSerializer(source='customer', read_only=True)
    sales_rep_detail = UserSerializer(source='sales_rep', read_only=True)
    activities = DealActivitySerializer(many=True, read_only=True)
    recent_activity = serializers.SerializerMethodField()

    class Meta:
        model = Deal
        fields = [
            'id',
            'customer',
            'customer_detail',
            'lead',
            'sales_rep',
            'sales_rep_detail',
            'stage',
            'value',
            'probability',
            'expected_close_date',
            'actual_close_date',
            'lost_reason',
            'lost_reason_detail',
            'notes',
            'activities',
            'recent_activity',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_recent_activity(self, obj):
        """Get most recent activity"""
        activity = obj.activities.first()
        if activity:
            return DealActivitySerializer(activity).data
        return None
