import {
  useState
} from 'react';

import {
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Compass,
  GitBranch
} from 'lucide-react';

import {
  misconceptionExplanation,
  skillLabel
} from '@/utils/skillLabels';


/* =========================================================
   DIAGNOSTIC ITEM
   ========================================================= */

function DiagnosticItem({
  icon: Icon,
  title,
  children,
  accent = 'cobalt'
}) {
  const accents = {
    cobalt:
      'border-cobalt-200 bg-cobalt-50/60 text-cobalt-700',

    amber:
      'border-amber-200 bg-amber-50/60 text-amber-700',

    teal:
      'border-teal-200 bg-teal-50/60 text-teal-700'
  };

  return (
    <div
      className={`rounded-xl border p-3.5 ${
        accents[accent]
      }`}
    >

      <div className="flex items-center gap-2">

        <Icon
          className="h-4 w-4"
          aria-hidden="true"
        />

        <span className="text-xs font-semibold uppercase tracking-wide">
          {title}
        </span>

      </div>


      <div className="mt-2 text-sm text-ink-700">
        {children}
      </div>

    </div>
  );
}


/* =========================================================
   FIND WHICH SKILL A MISCONCEPTION BELONGS TO
   ========================================================= */

function findMisconceptionSkill(
  misconceptionsBySkill,
  misconception
) {
  if (!misconceptionsBySkill) {
    return null;
  }

  for (
    const [
      skillId,
      skillMisconceptions
    ]
    of Object.entries(
      misconceptionsBySkill
    )
  ) {

    if (
      skillMisconceptions?.[
        misconception
      ] > 0
    ) {
      return skillId;
    }
  }

  return null;
}


/* =========================================================
   DIAGNOSTIC PANEL
   ========================================================= */

export default function DiagnosticPanel({
  diagnostics
}) {
  const [
    showDetails,
    setShowDetails
  ] = useState(false);


  if (!diagnostics) {
    return null;
  }


  /* =======================================================
     BACKEND RESPONSE FIELDS
     ======================================================= */

  const misconceptions =
    diagnostics.misconceptions || {};

  const misconceptionsBySkill =
    diagnostics
      .misconceptions_by_skill || {};

  const activeDiagnosis =
    diagnostics.active_diagnosis || null;

  const coldStart =
    diagnostics.cold_start || null;

  const possiblePivot =
    diagnostics
      .possible_prerequisite_pivot || null;


  /* =======================================================
     REPEATED MISCONCEPTIONS
     
     Backend stores these as:
     
     {
       "sign_error": 2,
       "inverse_operation_error": 3
     }
     
     We consider count >= 2 repeated evidence.
     ======================================================= */

  const repeatedMisconceptions =
    Object.entries(
      misconceptions
    )
      .filter(
        ([, count]) =>
          count >= 2
      )
      .map(
        ([
          misconception,
          count
        ]) => ({

          misconception,

          occurrences:
            count,

          skillId:
            findMisconceptionSkill(
              misconceptionsBySkill,
              misconception
            )
        })
      )
      .sort(
        (a, b) =>
          b.occurrences -
          a.occurrences
      );


  /* =======================================================
     COLD-START PROGRESS
     ======================================================= */

  const probeSkills =
    coldStart
      ?.probe_skills || [];

  const completedProbeSkills =
    coldStart
      ?.completed_probe_skills || [];

  const coldStartActive =
    coldStart &&
    coldStart.completed === false;


  /* =======================================================
     WHETHER PANEL HAS INTELLIGENCE TO DISPLAY
     ======================================================= */

  const hasItems =
    repeatedMisconceptions.length > 0 ||
    activeDiagnosis !== null ||
    coldStartActive ||
    possiblePivot !== null;


  return (
    <div className="space-y-3">

      <h3 className="text-sm font-semibold text-ink-800">
        What TutorTrace is noticing
      </h3>


      {/* ===================================================
          EMPTY STATE
          =================================================== */}

      {!hasItems && (

        <p className="text-sm text-ink-400">
          No active diagnostic patterns yet.
          As you answer more questions,
          TutorTrace will surface insights here.
        </p>

      )}


      {/* ===================================================
          REPEATED MISCONCEPTIONS
          =================================================== */}

      {repeatedMisconceptions.map(
        (item) => (

          <DiagnosticItem
            key={
              item.misconception
            }
            icon={
              AlertCircle
            }
            title="Pattern noticed"
            accent="amber"
          >

            <p className="font-medium text-ink-800">

              {misconceptionExplanation(
                item.misconception
              )}

            </p>


            {item.skillId && (

              <p className="mt-1 text-xs text-ink-500">

                In{' '}

                {skillLabel(
                  item.skillId
                )}

              </p>

            )}


            <p className="mt-1 text-xs text-ink-400">

              Seen{' '}

              {item.occurrences}

              {' '}

              {item.occurrences === 1
                ? 'time'
                : 'times'}

            </p>

          </DiagnosticItem>

        )
      )}


      {/* ===================================================
          ACTIVE PREREQUISITE DIAGNOSIS
          =================================================== */}

      {activeDiagnosis && (

        <DiagnosticItem
          icon={
            GitBranch
          }
          title="Checking a prerequisite"
          accent="cobalt"
        >

          <p>

            <span className="font-medium text-ink-800">

              {skillLabel(
                activeDiagnosis
                  .target_skill
              )}

            </span>

            {' '}
            may be blocked by{' '}

            <span className="font-medium text-ink-800">

              {skillLabel(
                activeDiagnosis
                  .diagnostic_skill
              )}

            </span>

            . TutorTrace is briefly
            checking that foundation.

          </p>

        </DiagnosticItem>

      )}


      {/* ===================================================
          COLD START
          =================================================== */}

      {coldStartActive && (

        <DiagnosticItem
          icon={
            Compass
          }
          title="Building your profile"
          accent="teal"
        >

          <p>

            TutorTrace is calibrating
            your starting mastery across
            key skills.

            {probeSkills.length > 0 && (

              <>

                {' '}

                {
                  completedProbeSkills
                    .length
                }

                /

                {
                  probeSkills.length
                }

                {' '}
                diagnostic probes completed.

              </>

            )}

          </p>

        </DiagnosticItem>

      )}


      {/* ===================================================
          OPTIONAL MODEL DETAILS
          =================================================== */}

      <button
        type="button"
        onClick={() =>
          setShowDetails(
            (value) =>
              !value
          )
        }
        className="inline-flex items-center gap-1 text-xs font-medium text-ink-400 transition-colors hover:text-ink-600 focus:outline-none focus-visible:underline"
      >

        {showDetails ? (

          <ChevronUp className="h-3.5 w-3.5" />

        ) : (

          <ChevronDown className="h-3.5 w-3.5" />

        )}

        Model details

      </button>


      {showDetails && (

        <pre className="max-h-64 overflow-auto rounded-xl border border-ink-200 bg-ink-50 p-3 text-xs text-ink-600 scrollbar-thin">

          {JSON.stringify(
            diagnostics,
            null,
            2
          )}

        </pre>

      )}

    </div>
  );
}