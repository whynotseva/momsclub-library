'use client'

import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import Placeholder from '@tiptap/extension-placeholder'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import Highlight from '@tiptap/extension-highlight'
import { useEffect, useRef } from 'react'

interface RichTextEditorProps {
  content: string
  onChange: (html: string) => void
  placeholder?: string
}

// Кнопка тулбара
const ToolbarButton = ({ 
  onClick, 
  isActive, 
  children, 
  title 
}: { 
  onClick: () => void
  isActive?: boolean
  children: React.ReactNode
  title: string
}) => (
  <button
    type="button"
    onClick={onClick}
    title={title}
    className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm transition-all ${
      isActive 
        ? 'bg-[#B08968] text-white shadow-sm' 
        : 'hover:bg-[#F5E6D3] text-[#5D4E3A]'
    }`}
  >
    {children}
  </button>
)

// Разделитель
const Divider = () => (
  <div className="w-px h-6 bg-[#E8D4BA]/50 mx-1" />
)

export default function RichTextEditor({ content, onChange, placeholder }: RichTextEditorProps) {
  // Ref для загрузки файлов (должен быть до любых условных return)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Underline,
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
      Highlight.configure({
        multicolor: true,
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-[#B08968] underline hover:text-[#8B6914]',
        },
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'rounded-xl max-w-full',
        },
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      Placeholder.configure({
        placeholder: placeholder || 'Начните писать или вставьте текст из Notion...',
      }),
    ],
    content: content,
    immediatelyRender: false, // Fix SSR hydration mismatch
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML())
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm max-w-none focus:outline-none min-h-[200px] px-4 py-3',
      },
    },
  })

  // Обновляем контент при изменении извне
  useEffect(() => {
    if (editor && content !== editor.getHTML()) {
      editor.commands.setContent(content)
    }
  }, [content, editor])

  if (!editor) {
    return (
      <div className="border border-[#E8D4BA]/50 rounded-xl p-4 animate-pulse bg-[#F5E6D3]/20">
        <div className="h-4 bg-[#E8D4BA]/30 rounded w-1/4 mb-2"></div>
        <div className="h-4 bg-[#E8D4BA]/30 rounded w-3/4"></div>
      </div>
    )
  }

  const addLink = () => {
    const url = window.prompt('Введите URL:')
    if (url) {
      editor.chain().focus().extendMarkRange('link').setLink({ href: url }).run()
    }
  }

  const addImageFromUrl = () => {
    const url = window.prompt('Введите URL изображения:')
    if (url) {
      editor.chain().focus().setImage({ src: url }).run()
    }
  }

  // Загрузка изображения с устройства
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Проверка типа
    if (!file.type.startsWith('image/')) {
      alert('Пожалуйста, выберите изображение')
      return
    }

    // Проверка размера (макс 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('Изображение слишком большое. Максимум 5 МБ')
      return
    }

    // Читаем как base64 для превью (в реальном приложении - загрузка на сервер)
    const reader = new FileReader()
    reader.onload = (event) => {
      const src = event.target?.result as string
      editor.chain().focus().setImage({ src }).run()
    }
    reader.readAsDataURL(file)
    
    // Сбрасываем input
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="border border-[#E8D4BA]/50 rounded-xl overflow-hidden bg-white">
      {/* Toolbar */}
      <div className="flex flex-wrap items-center gap-0.5 p-2 bg-[#F9F6F2] border-b border-[#E8D4BA]/30">
        {/* Заголовки */}
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          isActive={editor.isActive('heading', { level: 1 })}
          title="Заголовок 1"
        >
          H1
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          isActive={editor.isActive('heading', { level: 2 })}
          title="Заголовок 2"
        >
          H2
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          isActive={editor.isActive('heading', { level: 3 })}
          title="Заголовок 3"
        >
          H3
        </ToolbarButton>
        
        <Divider />
        
        {/* Форматирование текста */}
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          isActive={editor.isActive('bold')}
          title="Жирный (Ctrl+B)"
        >
          <span className="font-bold">B</span>
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          isActive={editor.isActive('italic')}
          title="Курсив (Ctrl+I)"
        >
          <span className="italic">I</span>
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          isActive={editor.isActive('underline')}
          title="Подчёркнутый (Ctrl+U)"
        >
          <span className="underline">U</span>
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleStrike().run()}
          isActive={editor.isActive('strike')}
          title="Зачёркнутый"
        >
          <span className="line-through">S</span>
        </ToolbarButton>
        
        <Divider />
        
        {/* Списки */}
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          isActive={editor.isActive('bulletList')}
          title="Маркированный список"
        >
          •≡
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          isActive={editor.isActive('orderedList')}
          title="Нумерованный список"
        >
          1.
        </ToolbarButton>
        
        <Divider />
        
        {/* Выравнивание */}
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('left').run()}
          isActive={editor.isActive({ textAlign: 'left' })}
          title="По левому краю"
        >
          ≡←
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('center').run()}
          isActive={editor.isActive({ textAlign: 'center' })}
          title="По центру"
        >
          ≡↔
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().setTextAlign('right').run()}
          isActive={editor.isActive({ textAlign: 'right' })}
          title="По правому краю"
        >
          ≡→
        </ToolbarButton>
        
        <Divider />
        
        {/* Вставки */}
        <ToolbarButton
          onClick={addLink}
          isActive={editor.isActive('link')}
          title="Вставить ссылку"
        >
          🔗
        </ToolbarButton>
        {/* Изображение с выпадающим меню */}
        <div className="relative group">
          <ToolbarButton
            onClick={() => {}}
            isActive={false}
            title="Вставить изображение"
          >
            🖼
          </ToolbarButton>
          <div className="absolute top-full left-0 mt-1 bg-white rounded-lg shadow-xl border border-[#E8D4BA]/50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 min-w-[160px]">
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="w-full px-3 py-2 text-left text-sm text-[#5D4E3A] hover:bg-[#F5E6D3] flex items-center gap-2 rounded-t-lg"
            >
              📤 С устройства
            </button>
            <button
              type="button"
              onClick={addImageFromUrl}
              className="w-full px-3 py-2 text-left text-sm text-[#5D4E3A] hover:bg-[#F5E6D3] flex items-center gap-2 rounded-b-lg"
            >
              🔗 По URL
            </button>
          </div>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
        />
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
          isActive={editor.isActive('blockquote')}
          title="Цитата"
        >
          ❝
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleCodeBlock().run()}
          isActive={editor.isActive('codeBlock')}
          title="Блок кода"
        >
          {'</>'}
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().setHorizontalRule().run()}
          isActive={false}
          title="Разделитель"
        >
          ―
        </ToolbarButton>
        
        <Divider />
        
        {/* Чеклист и выделение */}
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleTaskList().run()}
          isActive={editor.isActive('taskList')}
          title="Чек-лист (To-do)"
        >
          ☑️
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHighlight({ color: '#FEF3C7' }).run()}
          isActive={editor.isActive('highlight')}
          title="Выделить жёлтым"
        >
          🟡
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHighlight({ color: '#DCFCE7' }).run()}
          isActive={false}
          title="Выделить зелёным"
        >
          🟢
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHighlight({ color: '#FEE2E2' }).run()}
          isActive={false}
          title="Выделить красным"
        >
          🔴
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHighlight({ color: '#DBEAFE' }).run()}
          isActive={false}
          title="Выделить синим"
        >
          🔵
        </ToolbarButton>
        
        <Divider />
        
        {/* Отмена/повтор */}
        <ToolbarButton
          onClick={() => editor.chain().focus().undo().run()}
          isActive={false}
          title="Отменить (Ctrl+Z)"
        >
          ↩
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().redo().run()}
          isActive={false}
          title="Повторить (Ctrl+Y)"
        >
          ↪
        </ToolbarButton>
      </div>
      
      {/* Editor */}
      <EditorContent editor={editor} />
      
      {/* Подсказка */}
      <div className="px-4 py-2 bg-[#F9F6F2] border-t border-[#E8D4BA]/30 text-xs text-[#8B8279]">
        💡 Совет: Вставляйте текст напрямую из Notion — форматирование сохранится!
      </div>
    </div>
  )
}
