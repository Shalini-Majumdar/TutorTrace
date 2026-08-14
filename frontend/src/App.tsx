import { useState } from 'react';
import { Brain, GraduationCap, LayoutDashboard } from 'lucide-react';
import StudentSession from '@/pages/StudentSession';
import TeacherDashboard from '@/pages/TeacherDashboard';

const TABS = [
  { key: 'student', label: 'Student Experience', icon: GraduationCap },
  { key: 'teacher', label: 'Teacher Dashboard', icon: LayoutDashboard },
];

function App() {
  const [tab, setTab] = useState('student');

  return (
    <div className="min-h-screen bg-[#f7f8fa]">
      <header className="sticky top-0 z-20 border-b border-ink-200 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cobalt-600 text-white">
              <Brain className="h-5 w-5" aria-hidden="true" />
            </div>
            <div className="leading-tight">
              <div className="font-serif text-lg font-semibold text-ink-900">TutorTrace</div>
              <div className="text-[11px] font-medium uppercase tracking-wide text-cobalt-600">
                Adaptive Learning Intelligence
              </div>
            </div>
          </div>

          <nav className="flex items-center gap-1 rounded-xl border border-ink-200 bg-ink-50 p-1">
            {TABS.map(({ key, label, icon: Icon }) => (
              <button
                key={key}
                type="button"
                onClick={() => setTab(key)}
                aria-pressed={tab === key}
                className={`inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-cobalt-400 ${
                  tab === key
                    ? 'bg-white text-cobalt-700 shadow-sm'
                    : 'text-ink-500 hover:text-ink-700'
                }`}
              >
                <Icon className="h-4 w-4" aria-hidden="true" />
                <span className="hidden sm:inline">{label}</span>
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main>
        {tab === 'student' ? <StudentSession /> : <TeacherDashboard />}
      </main>
    </div>
  );
}

export default App;
