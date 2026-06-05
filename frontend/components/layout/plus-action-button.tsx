'use client';

import { ChangeEvent, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { FileUp, Plus } from 'lucide-react';
import { getBackendUrl } from '@/lib/backend';

type PlusActionButtonProps = {
  label: string;
};

export function PlusActionButton({ label }: PlusActionButtonProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleClick() {
    const text = window.prompt('Вставьте описание проекта:');
    const backendUrl = getBackendUrl();

    if (!text || !text.trim()) return;
    if (!backendUrl) {
      alert('Не задан NEXT_PUBLIC_BACKEND_URL');
      return;
    }

    try {
      const res = await fetch(`${backendUrl}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        alert(`Ошибка: ${data.error || 'Не удалось выполнить расчёт'}`);
        return;
      }

      alert('Проект успешно создан');
      window.location.href = '/projects';
    } catch {
      alert('Ошибка запроса к backend');
    }
  }

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    const backendUrl = getBackendUrl();

    if (!file) return;
    if (!backendUrl) {
      alert('Не задан NEXT_PUBLIC_BACKEND_URL');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${backendUrl}/analyze-file`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();

      if (!res.ok || !data.success) {
        alert(`Ошибка: ${data.error || 'Не удалось выполнить расчёт файла'}`);
        return;
      }

      alert('Проект из файла успешно создан');
      window.location.href = '/projects';
    } catch {
      alert('Ошибка запроса к backend');
    } finally {
      event.target.value = '';
    }
  }

  return (
    <div className="flex flex-wrap gap-2 self-start">
      <Button onClick={handleClick} className="gap-2">
        <Plus className="h-4 w-4" />
        {label}
      </Button>
      <Button variant="outline" onClick={() => fileInputRef.current?.click()} className="gap-2">
        <FileUp className="h-4 w-4" />
        Файл
      </Button>
      <input
        ref={fileInputRef}
        type="file"
        className="hidden"
        accept=".txt,.json,.csv,.docx,.pdf"
        onChange={handleFileChange}
      />
    </div>
  );
}
