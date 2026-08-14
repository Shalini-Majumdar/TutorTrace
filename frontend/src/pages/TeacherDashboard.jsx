import {
  useCallback,
  useEffect,
  useMemo,
  useState
} from 'react';

import {
  AlertTriangle,
  Users
} from 'lucide-react';

import * as api from '@/api/tutorTraceApi';

import TeacherAlerts from '@/components/TeacherAlerts';
import TeacherHeatmap from '@/components/TeacherHeatmap';
import StudentDetailPanel from '@/components/StudentDetailPanel';
import ErrorState from '@/components/ErrorState';
import Skeleton from '@/components/Skeleton';


export default function TeacherDashboard() {
  const [classroom, setClassroom] =
    useState(null);

  const [alerts, setAlerts] =
    useState([]);

  const [error, setError] =
    useState(null);

  const [
    selectedStudentId,
    setSelectedStudentId
  ] = useState(null);

  const [loading, setLoading] =
    useState(true);


  const load =
    useCallback(async () => {
      setLoading(true);
      setError(null);

      try {
        const [
          classroomResponse,
          alertsResponse
        ] = await Promise.all([
          api.getTeacherClassroom(),
          api.getTeacherAlerts()
        ]);


        setClassroom(
          classroomResponse
        );


        /*
         * Support either:
         *
         * [...]
         *
         * or:
         *
         * {
         *   alerts: [...]
         * }
         */
        if (
          Array.isArray(
            alertsResponse
          )
        ) {
          setAlerts(
            alertsResponse
          );
        } else if (
          Array.isArray(
            alertsResponse?.alerts
          )
        ) {
          setAlerts(
            alertsResponse.alerts
          );
        } else {
          setAlerts([]);
        }

      } catch (err) {
        setError(err);

      } finally {
        setLoading(false);
      }
    }, []);


  useEffect(() => {
    load();
  }, [load]);


  /*
   * Find selected student's ROW INDEX.
   *
   * This is important because:
   *
   * classroom.students[rowIndex]
   * corresponds exactly to
   * classroom.matrix[rowIndex].
   */
  const selectedStudentIndex =
    useMemo(() => {
      if (
        !Array.isArray(
          classroom?.students
        ) ||
        !selectedStudentId
      ) {
        return -1;
      }

      return classroom.students.findIndex(
        (student) =>
          student.student_id ===
          selectedStudentId
      );
    }, [
      classroom,
      selectedStudentId
    ]);


  const selectedStudent =
    selectedStudentIndex >= 0
      ? classroom.students[
          selectedStudentIndex
        ]
      : null;


  const selectedMasteryRow =
    selectedStudentIndex >= 0
      ? classroom?.matrix?.[
          selectedStudentIndex
        ] || []
      : [];


  const skills =
    Array.isArray(
      classroom?.skills
    )
      ? classroom.skills
      : [];


  return (
    <div className="mx-auto max-w-7xl px-4 py-6">

      {/* ===================================================
          HEADER
          =================================================== */}

      <header className="mb-6">

        <div className="flex flex-wrap items-center gap-3">

          <h1 className="font-serif text-2xl font-medium text-ink-900">
            Classroom Intelligence
          </h1>

          <span className="inline-flex items-center gap-1 rounded-full border border-ink-200 bg-ink-50 px-2.5 py-0.5 text-xs font-medium text-ink-500">
            Simulated classroom data
          </span>

        </div>


        <p className="mt-1 text-sm text-ink-500">
          Where does the class need intervention right now?
        </p>

      </header>


      {/* ===================================================
          ERROR
          =================================================== */}

      {error && (

        <div className="mb-6">

          <ErrorState
            error={error}
            onRetry={load}
            retryLabel="Reload dashboard"
          />

        </div>

      )}


      {/* ===================================================
          LOADING
          =================================================== */}

      {loading && (

        <div className="space-y-6">

          <div className="space-y-3">

            <Skeleton className="h-20 w-full" />

            <Skeleton className="h-20 w-full" />

          </div>

          <Skeleton className="h-64 w-full" />

        </div>

      )}


      {/* ===================================================
          MAIN DASHBOARD
          =================================================== */}

      {!loading &&
        !error &&
        classroom && (

        <div className="space-y-6">


          {/* ===============================================
              INTERVENTION ALERTS
              =============================================== */}

          <section
            aria-label="Intervention alerts"
          >

            <div className="mb-3 flex items-center gap-2">

              <AlertTriangle
                className="h-4 w-4 text-coral-500"
                aria-hidden="true"
              />

              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
                Intervention alerts
              </h2>

            </div>


            <TeacherAlerts
              alerts={alerts}
            />

          </section>


          {/* ===============================================
              CLASSROOM MASTERY MATRIX
              =============================================== */}

          <section
            aria-label="Classroom mastery matrix"
          >

            <div className="mb-3 flex items-center gap-2">

              <Users
                className="h-4 w-4 text-cobalt-500"
                aria-hidden="true"
              />

              <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
                Mastery matrix
              </h2>

            </div>


            <div className="rounded-2xl border border-ink-200 bg-white p-4 shadow-card">

              <TeacherHeatmap
                classroom={
                  classroom
                }
                onSelectStudent={
                  setSelectedStudentId
                }
                selectedStudentId={
                  selectedStudentId
                }
              />

            </div>


            <p className="mt-2 text-xs text-ink-400">
              Click a student name to see their detail.
              Each cell shows effective mastery — color
              intensity reflects readiness.
            </p>

          </section>


          {/* ===============================================
              STUDENT DETAIL
              =============================================== */}

          {selectedStudent && (

            <div className="lg:fixed lg:right-4 lg:top-20 lg:z-30 lg:w-80">

              <StudentDetailPanel
                student={
                  selectedStudent
                }
                skills={
                  skills
                }
                masteryRow={
                  selectedMasteryRow
                }
                onClose={() =>
                  setSelectedStudentId(
                    null
                  )
                }
              />

            </div>

          )}

        </div>

      )}

    </div>
  );
}