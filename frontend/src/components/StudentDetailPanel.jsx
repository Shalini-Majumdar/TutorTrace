import {
  X,
  GraduationCap
} from 'lucide-react';

import {
  skillLabel
} from '@/utils/skillLabels';

import {
  toPercentage
} from '@/utils/formatters';

import MasteryBar from './MasteryBar';


export default function StudentDetailPanel({
  student,
  skills = [],
  masteryRow = [],
  onClose
}) {
  if (!student) {
    return null;
  }


  const masteryEntries =
    skills.map((skillId, index) => ({
      skillId,
      mastery:
        typeof masteryRow[index] === 'number'
          ? masteryRow[index]
          : null
    }));


  return (
    <aside className="animate-scale-in flex flex-col rounded-2xl border border-ink-200 bg-white shadow-card lg:sticky lg:top-4">

      <header className="flex items-center justify-between border-b border-ink-100 p-4">

        <div>

          <h3 className="text-base font-semibold text-ink-900">
            {student.name ||
              student.student_id}
          </h3>

          <p className="text-xs text-ink-400">
            ID: {student.student_id}
          </p>

        </div>


        <button
          type="button"
          onClick={onClose}
          className="rounded-lg p-1.5 text-ink-400 transition-colors hover:bg-ink-100 hover:text-ink-700 focus:outline-none focus-visible:ring-2 focus-visible:ring-ink-300"
          aria-label="Close student details"
        >
          <X className="h-4 w-4" />
        </button>

      </header>


      <div className="flex-1 space-y-5 p-4">

        <div className="flex items-center gap-2.5 rounded-xl bg-ink-50 p-3">

          <GraduationCap
            className="h-4 w-4 text-ink-400"
            aria-hidden="true"
          />

          <div>

            <p className="text-xs font-semibold uppercase tracking-wide text-ink-400">
              Mastery profile
            </p>

            <p className="text-sm text-ink-600">
              Effective mastery by skill
            </p>

          </div>

        </div>


        <div className="space-y-3">

          {masteryEntries.map(
            ({
              skillId,
              mastery
            }) => (

              <div
                key={skillId}
                className="rounded-lg border border-ink-100 p-3"
              >

                <div className="mb-1.5 flex items-center justify-between gap-3">

                  <span className="text-sm font-medium text-ink-700">
                    {skillLabel(skillId)}
                  </span>


                  <span className="text-xs font-semibold tabular-nums text-ink-500">

                    {mastery != null
                      ? `${toPercentage(
                          mastery
                        )}%`
                      : '—'}

                  </span>

                </div>


                {mastery != null && (

                  <MasteryBar
                    value={mastery}
                    showLabel={false}
                    animate={false}
                    size="sm"
                  />

                )}

              </div>

            )
          )}

        </div>

      </div>

    </aside>
  );
}