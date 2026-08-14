import { Sparkles } from 'lucide-react';

import {
  selectionReasonCopy
} from '@/utils/skillLabels';


export default function SelectionReason({
  reason
}) {
  if (!reason) {
    return null;
  }

  /*
   * Backend SelectionReason uses:
   *
   * {
   *   type: "...",
   *   ...
   * }
   *
   * NOT selection_type.
   */
  const copy =
    selectionReasonCopy(
      reason.type
    );


  return (
    <div className="rounded-xl border border-ink-200 bg-ink-50/60 p-3.5">

      <div className="flex items-center gap-2">

        <Sparkles
          className="h-4 w-4 text-cobalt-500"
          aria-hidden="true"
        />

        <span className="text-xs font-semibold uppercase tracking-wide text-cobalt-600">
          Why this question?
        </span>

      </div>


      <p className="mt-2 text-sm text-ink-700">
        {copy}
      </p>


      {reason.type === 'cold_start' &&
        reason.probe_number != null &&
        reason.total_probes != null && (

          <p className="mt-1.5 text-xs text-ink-400">
            Diagnostic probe{' '}
            <span className="font-medium text-ink-600">
              {reason.probe_number}
            </span>
            {' '}of{' '}
            <span className="font-medium text-ink-600">
              {reason.total_probes}
            </span>
          </p>

        )}

    </div>
  );
}