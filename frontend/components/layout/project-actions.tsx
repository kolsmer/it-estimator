'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { getBackendUrl } from '@/lib/backend';

type ProjectActionsProps = {
  projectId: string;
  projectName: string;
  initialStatus: 'active' | 'archived';
  onStatusChange?: (status: 'active' | 'archived') => void;
  onDeleted?: () => void;
};

function actionLabel(action: string) {
  if (action === 'archive') return 'Архивировать';
  if (action === 'restore') return 'Восстановить';
  return 'Удалить';
}

export function ProjectActions({ projectId, projectName, initialStatus, onStatusChange, onDeleted }: ProjectActionsProps) {
  const [status, setStatus] = useState<'active' | 'archived'>(initialStatus);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const backendUrl = getBackendUrl();

  async function runAction(action: 'archive' | 'restore' | 'delete') {
    if (!backendUrl) {
      window.alert('Не задан NEXT_PUBLIC_BACKEND_URL');
      return;
    }

    if (action === 'delete' && !window.confirm(`Удалить проект «${projectName}»?`)) {
      return;
    }

    setBusyAction(action);

    try {
      const response = await fetch(
        action === 'delete' ? `${backendUrl}/projects/${projectId}` : `${backendUrl}/projects/${projectId}/${action}`,
        {
          method: action === 'delete' ? 'DELETE' : 'POST',
          headers: { Accept: 'application/json' }
        }
      );

      const payload = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(payload.detail || payload.message || 'Не удалось выполнить действие');
      }

      if (action === 'archive') {
        setStatus('archived');
        onStatusChange?.('archived');
      }

      if (action === 'restore') {
        setStatus('active');
        onStatusChange?.('active');
      }

      if (action === 'delete') {
        onDeleted?.();
        return;
      }

      window.alert(payload.message || `${actionLabel(action)} выполнено`);
    } catch (error) {
      window.alert(error instanceof Error ? error.message : 'Не удалось выполнить действие');
    } finally {
      setBusyAction(null);
    }
  }

  return (
    <div className="flex flex-wrap gap-3">
      <Button variant="outline" onClick={() => runAction('archive')} disabled={busyAction !== null || status === 'archived'}>
        Архивировать
      </Button>
      <Button variant="secondary" onClick={() => runAction('restore')} disabled={busyAction !== null || status === 'active'}>
        Восстановить
      </Button>
      <Button variant="outline" onClick={() => runAction('delete')} disabled={busyAction !== null}>
        Удалить
      </Button>
    </div>
  );
}