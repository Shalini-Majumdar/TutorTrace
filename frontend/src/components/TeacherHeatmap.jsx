import { skillLabel } from '@/utils/skillLabels';
import {
  masteryBand,
  toPercentage
} from '@/utils/formatters';


const BAND_STYLES = {
  coral: {
    bg: 'bg-coral-100',
    bar: 'bg-coral-500',
    text: 'text-coral-700',
    hover: 'hover:bg-coral-200'
  },

  amber: {
    bg: 'bg-amber-100',
    bar: 'bg-amber-500',
    text: 'text-amber-700',
    hover: 'hover:bg-amber-200'
  },

  teal: {
    bg: 'bg-teal-100',
    bar: 'bg-teal-500',
    text: 'text-teal-700',
    hover: 'hover:bg-teal-200'
  },

  sage: {
    bg: 'bg-sage-100',
    bar: 'bg-sage-500',
    text: 'text-sage-700',
    hover: 'hover:bg-sage-200'
  },

  ink: {
    bg: 'bg-ink-100',
    bar: 'bg-ink-300',
    text: 'text-ink-500',
    hover: 'hover:bg-ink-200'
  }
};


function getSkillId(skill) {
  if (typeof skill === 'string') {
    return skill;
  }

  if (
    skill &&
    typeof skill === 'object'
  ) {
    return (
      skill.skill_id ??
      skill.id ??
      skill.name ??
      ''
    );
  }

  return '';
}


function MasteryCell({
  value,
  skillId,
  studentName
}) {
  const safeValue =
    typeof value === 'number'
      ? Math.min(
          1,
          Math.max(0, value)
        )
      : 0;


  const band =
    masteryBand(
      safeValue
    );

  const styles =
    BAND_STYLES[
      band.color
    ] ||
    BAND_STYLES.ink;

  const pct =
    toPercentage(
      safeValue
    );


  return (
    <td className="p-1">

      <div
        className={`relative h-12 min-w-[3.5rem] cursor-default rounded-lg ${styles.bg} ${styles.hover} transition-colors`}
        title={`${studentName} — ${
          skillId
            ? skillLabel(skillId)
            : 'Unknown skill'
        }: ${pct}% (${band.label})`}
      >

        <div className="flex h-full flex-col items-center justify-center gap-1">

          <span
            className={`text-sm font-bold tabular-nums ${styles.text}`}
          >
            {pct}%
          </span>


          <div className="h-1 w-8 overflow-hidden rounded-full bg-black/10">

            <div
              className={`h-full ${styles.bar}`}
              style={{
                width: `${pct}%`
              }}
            />

          </div>

        </div>


        <span className="sr-only">
          {band.label}
        </span>

      </div>

    </td>
  );
}


export default function TeacherHeatmap({
  classroom,
  onSelectStudent,
  selectedStudentId
}) {
  if (!classroom) {
    return null;
  }


  const students =
    Array.isArray(
      classroom.students
    )
      ? classroom.students
      : [];


  /*
   * IMPORTANT:
   *
   * Preserve the exact original array order
   * because matrix columns correspond to
   * classroom.skills by index.
   *
   * We only convert each element into its
   * string skill ID.
   */
  const skills =
    Array.isArray(
      classroom.skills
    )
      ? classroom.skills.map(
          getSkillId
        )
      : [];


  const matrix =
    Array.isArray(
      classroom.matrix
    )
      ? classroom.matrix
      : [];


  return (
    <div className="overflow-x-auto scrollbar-thin">

      <table className="w-full border-separate border-spacing-0">

        <thead>

          <tr>

            <th className="sticky left-0 z-10 bg-[#f7f8fa] px-3 py-2 text-left">

              <span className="text-xs font-semibold uppercase tracking-wide text-ink-400">
                Student
              </span>

            </th>


            {skills.map(
              (skillId, colIdx) => (

                <th
                  key={
                    skillId ||
                    `skill-${colIdx}`
                  }
                  className="px-1 py-2 text-center"
                >

                  <div className="flex h-12 w-14 items-center justify-center">

                    <span className="text-[11px] font-semibold leading-tight text-ink-500">

                      {skillId
                        ? skillLabel(
                            skillId
                          )
                        : 'Unknown'}

                    </span>

                  </div>

                </th>

              )
            )}

          </tr>

        </thead>


        <tbody>

          {students.map(
            (student, rowIdx) => {

              const studentId =
                student.student_id;

              const studentName =
                student.name ||
                studentId;

              const isSelected =
                selectedStudentId ===
                studentId;


              return (
                <tr
                  key={
                    studentId ||
                    rowIdx
                  }
                >

                  <td className="sticky left-0 z-10 bg-[#f7f8fa] px-3 py-1">

                    <button
                      type="button"
                      onClick={() =>
                        onSelectStudent?.(
                          studentId
                        )
                      }
                      className={`flex items-center gap-2 rounded-lg px-2 py-1.5 text-left transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-cobalt-400 ${
                        isSelected
                          ? 'bg-cobalt-100 text-cobalt-800'
                          : 'text-ink-700 hover:bg-ink-100'
                      }`}
                    >

                      <span className="text-sm font-medium">
                        {studentName}
                      </span>

                    </button>

                  </td>


                  {skills.map(
                    (
                      skillId,
                      colIdx
                    ) => (

                      <MasteryCell
                        key={
                          skillId ||
                          colIdx
                        }
                        value={
                          matrix?.[
                            rowIdx
                          ]?.[
                            colIdx
                          ]
                        }
                        skillId={
                          skillId
                        }
                        studentName={
                          studentName
                        }
                      />

                    )
                  )}

                </tr>
              );
            }
          )}

        </tbody>

      </table>

    </div>
  );
}