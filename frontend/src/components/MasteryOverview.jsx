import { skillLabel } from '@/utils/skillLabels';
import {
  masteryBand,
  toPercentage
} from '@/utils/formatters';

import MasteryBar from './MasteryBar';


const BAND_DOT = {
  coral: 'bg-coral-500',
  amber: 'bg-amber-500',
  teal: 'bg-teal-500',
  sage: 'bg-sage-500',
  ink: 'bg-ink-300',
};


export default function MasteryOverview({
  mastery,
  skillOrder,
  activeSkillId
}) {
  if (!mastery?.skills) {
    return null;
  }

  /*
   * Backend shape:
   *
   * mastery.skills = {
   *   integer_operations: {
   *     stored_mastery: ...,
   *     effective_mastery: ...
   *   },
   *   ...
   * }
   *
   * So we access by key instead of using .find().
   */
  const skills = skillOrder.map((id) => {
    const entry =
      mastery.skills[id] || null;

    return {
      id,
      ...(entry || {})
    };
  });


  return (
    <div className="space-y-3">

      <h3 className="text-sm font-semibold text-ink-800">
        Skill mastery
      </h3>

      <div className="space-y-3">

        {skills.map((skill) => {

          /*
           * A skill should normally always have
           * effective_mastery, but defaulting to
           * 0 keeps the UI safe if data is missing.
           */
          const effectiveMastery =
            typeof skill.effective_mastery === 'number'
              ? skill.effective_mastery
              : 0;

          const band =
            masteryBand(
              effectiveMastery
            );

          const isActive =
            skill.id ===
            activeSkillId;


          return (
            <div
              key={skill.id}
              className={`rounded-lg p-2 transition-colors ${
                isActive
                  ? 'bg-cobalt-50 ring-1 ring-cobalt-200'
                  : ''
              }`}
            >

              <div className="mb-1.5 flex items-center justify-between gap-2">

                <div className="flex min-w-0 items-center gap-2">

                  <span
                    className={`h-2 w-2 shrink-0 rounded-full ${
                      BAND_DOT[
                        band.color
                      ] ||
                      'bg-ink-300'
                    }`}
                  />

                  <span className="truncate text-sm font-medium text-ink-700">
                    {skillLabel(
                      skill.id
                    )}
                  </span>

                </div>


                <span className="shrink-0 text-xs font-semibold tabular-nums text-ink-600">
                  {toPercentage(
                    effectiveMastery
                  )}
                  %
                </span>

              </div>


              <MasteryBar
                value={
                  effectiveMastery
                }
                showLabel={
                  false
                }
                size="sm"
              />

            </div>
          );
        })}

      </div>

    </div>
  );
}