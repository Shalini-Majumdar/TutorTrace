import {
  AlertOctagon,
  AlertTriangle,
  Lightbulb
} from 'lucide-react';

import {
  skillLabel
} from '@/utils/skillLabels';


const SEVERITY = {
  high: {
    label: 'High priority',
    icon: AlertOctagon,
    container: 'border-coral-300 bg-coral-50',
    badge: 'bg-coral-600 text-white',
    text: 'text-coral-800',
  },

  medium: {
    label: 'Medium priority',
    icon: AlertTriangle,
    container: 'border-amber-300 bg-amber-50/70',
    badge: 'bg-amber-500 text-white',
    text: 'text-amber-800',
  },

  low: {
    label: 'Low priority',
    icon: AlertTriangle,
    container: 'border-ink-200 bg-ink-50',
    badge: 'bg-ink-500 text-white',
    text: 'text-ink-700',
  },
};


function formatPercentage(value) {
  if (
    typeof value !== 'number' ||
    Number.isNaN(value)
  ) {
    return null;
  }

  /*
   * Supports either backend form:
   *
   * 0.7  -> 70%
   * 70   -> 70%
   */
  if (value <= 1) {
    return Math.round(value * 100);
  }

  return Math.round(value);
}


export default function TeacherAlerts({
  alerts
}) {
  if (
    !Array.isArray(alerts) ||
    alerts.length === 0
  ) {
    return (
      <div className="rounded-xl border border-sage-200 bg-sage-50/60 p-4">

        <div className="flex items-center gap-2">

          <Lightbulb
            className="h-4 w-4 text-sage-600"
            aria-hidden="true"
          />

          <p className="text-sm font-medium text-sage-800">
            No active intervention alerts.
            The classroom is progressing well.
          </p>

        </div>

      </div>
    );
  }


  return (
    <div className="space-y-3">

      {alerts.map((alert, index) => {

        const severity =
          SEVERITY[alert.severity] ||
          SEVERITY.medium;

        const Icon =
          severity.icon;

        const lowMasteryPercent =
          formatPercentage(
            alert.low_mastery_percentage
          );


        return (
          <div
            key={
              alert.skill_id ||
              index
            }
            className={`animate-fade-in rounded-xl border-2 p-4 ${
              severity.container
            }`}
            role="alert"
          >

            <div className="flex flex-wrap items-center gap-2">

              <span
                className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-bold uppercase tracking-wide ${
                  severity.badge
                }`}
              >

                <Icon
                  className="h-3 w-3"
                  aria-hidden="true"
                />

                {severity.label}

              </span>


              {alert.skill_id && (

                <span className="text-base font-semibold text-ink-900">

                  {skillLabel(
                    alert.skill_id
                  )}

                </span>

              )}

            </div>


            <p
              className={`mt-2 text-sm font-medium ${
                severity.text
              }`}
            >

              {lowMasteryPercent != null
                ? `${lowMasteryPercent}% of learners are below the mastery threshold`
                : 'Some learners are below the mastery threshold'}

            </p>


            {alert.recommendation && (

              <div className="mt-3 flex items-start gap-2 rounded-lg bg-white/70 p-3">

                <Lightbulb
                  className="mt-0.5 h-4 w-4 shrink-0 text-cobalt-600"
                  aria-hidden="true"
                />


                <div>

                  <p className="text-xs font-semibold uppercase tracking-wide text-ink-400">
                    Recommended intervention
                  </p>

                  <p className="mt-0.5 text-sm text-ink-700">
                    {alert.recommendation}
                  </p>

                </div>

              </div>

            )}

          </div>
        );
      })}

    </div>
  );
}