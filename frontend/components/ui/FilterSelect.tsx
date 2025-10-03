'use client';

import { Listbox, Transition } from '@headlessui/react';
import { ChevronDown } from 'lucide-react';
import { Fragment } from 'react';

export type Option = { value: string; label: string };

export default function FilterSelect({
  value,
  onChange,
  options,
  placeholder = 'Select',
  className = '',
  widthClass = 'w-48',
}: {
  value: string;
  onChange: (v: string) => void;
  options: Option[];
  placeholder?: string;
  className?: string;
  widthClass?: string;
}) {
  const selected = options.find(o => o.value === value);

  return (
    <Listbox value={value} onChange={onChange}>
      <div className={`relative ${widthClass} ${className}`}>
        <Listbox.Button
          className="inline-flex items-center justify-between rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        >
          <span className={`truncate ${selected ? 'text-gray-900' : 'text-gray-500'}`}>
            {selected?.label ?? placeholder}
          </span>
          <ChevronDown size={16} />
        </Listbox.Button>

        <Transition
          as={Fragment}
          enter="transition ease-out duration-100"
          enterFrom="opacity-0 scale-95"
          enterTo="opacity-100 scale-100"
          leave="transition ease-in duration-75"
          leaveFrom="opacity-100 scale-100"
          leaveTo="opacity-0 scale-95"
        >
          <Listbox.Options className="absolute z-20 mt-1 max-h-60 w-full overflow-auto rounded-md border border-gray-200 bg-white py-1 text-sm shadow-lg">
            {/* Optional "All" */}
            <Listbox.Option
              key="__all__"
              value=""
              className={({ active, selected }) =>
                `cursor-pointer px-3 py-2 ${active ? 'bg-gray-100' : ''} ${selected ? 'font-medium' : ''} text-gray-900`
              }
            >
              All
            </Listbox.Option>

            {options.map(o => (
              <Listbox.Option
                key={o.value}
                value={o.value}
                className={({ active, selected }) =>
                  `cursor-pointer px-3 py-2 ${active ? 'bg-gray-100' : ''} ${selected ? 'font-medium' : ''} text-gray-900`
                }
              >
                {o.label}
              </Listbox.Option>
            ))}
          </Listbox.Options>
        </Transition>
      </div>
    </Listbox>
  );
}
