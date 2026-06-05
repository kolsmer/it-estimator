import { Sidebar } from '@/components/layout/sidebar';

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-950 to-slate-900">
      <div className="mx-auto flex w-full max-w-[1600px]">
        <Sidebar />
        <main className="min-h-screen flex-1 p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}
