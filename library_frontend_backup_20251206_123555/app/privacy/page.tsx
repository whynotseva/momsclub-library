'use client'

import Link from 'next/link'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#FDFCFA] via-[#FBF8F3] to-[#F5EFE6]">
      {/* Header */}
      <header className="w-full px-6 py-8 border-b border-gray-200/50">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link href="/login" className="group relative">
            <img 
              src="/logolibrary.svg" 
              alt="LibriMomsClub" 
              className="h-10 w-auto group-hover:scale-105 transition-transform"
            />
          </Link>
          <Link 
            href="/login"
            className="text-sm font-medium text-[#B08968] hover:text-[#8B7355] transition-colors"
          >
            ← Назад
          </Link>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 py-12">
        <h1 className="text-3xl font-bold text-[#2D2A26] mb-8">Политика конфиденциальности</h1>
        
        <div className="prose prose-lg max-w-none text-[#5C5650] space-y-6">
          <p className="text-sm text-[#8B8279]">Дата последнего обновления: 1 декабря 2025 года</p>
          
          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">1. Общие положения</h2>
            <p>
              Настоящая Политика конфиденциальности (далее — «Политика») определяет порядок обработки 
              и защиты персональных данных пользователей сервиса LibriMomsClub (далее — «Сервис»), 
              принадлежащего Самозанятая Дмитренко Полина Андреевна (далее — «Оператор»).
            </p>
            <p>
              Использование Сервиса означает безоговорочное согласие пользователя с настоящей Политикой 
              и указанными в ней условиями обработки персональных данных.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">2. Персональные данные, которые мы собираем</h2>
            <p>При использовании Сервиса мы можем собирать следующие данные:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Идентификатор пользователя Telegram (Telegram ID)</li>
              <li>Имя и фамилия (из профиля Telegram)</li>
              <li>Имя пользователя (username) в Telegram</li>
              <li>Фотография профиля (если доступна)</li>
              <li>Данные об активности в Сервисе (просмотренные материалы, избранное)</li>
              <li>Техническая информация (IP-адрес, тип браузера, время доступа)</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">3. Цели обработки персональных данных</h2>
            <p>Мы используем ваши данные для:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Идентификации и авторизации пользователей</li>
              <li>Предоставления доступа к контенту библиотеки</li>
              <li>Персонализации пользовательского опыта</li>
              <li>Улучшения качества Сервиса</li>
              <li>Связи с пользователями по вопросам поддержки</li>
              <li>Выполнения договорных обязательств по подписке</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">4. Защита персональных данных</h2>
            <p>
              Оператор принимает необходимые организационные и технические меры для защиты 
              персональных данных от неправомерного доступа, уничтожения, изменения, блокирования, 
              копирования, распространения, а также от иных неправомерных действий третьих лиц.
            </p>
            <p>
              Данные хранятся на защищённых серверах с использованием современных методов шифрования.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">5. Передача данных третьим лицам</h2>
            <p>
              Мы не передаём ваши персональные данные третьим лицам, за исключением случаев:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Когда это необходимо для оказания услуг (платёжные системы)</li>
              <li>По требованию законодательства Российской Федерации</li>
              <li>С вашего явного согласия</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">6. Права пользователей</h2>
            <p>Вы имеете право:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Получить информацию о хранящихся персональных данных</li>
              <li>Требовать исправления неточных данных</li>
              <li>Требовать удаления ваших данных</li>
              <li>Отозвать согласие на обработку данных</li>
            </ul>
            <p>
              Для реализации этих прав обратитесь в поддержку: 
              <a href="https://t.me/momsclubsupport" className="text-[#B08968] hover:underline ml-1">@momsclubsupport</a>
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">7. Cookies и аналитика</h2>
            <p>
              Сервис использует файлы cookies и аналогичные технологии для обеспечения работы 
              авторизации и улучшения пользовательского опыта. Вы можете отключить cookies 
              в настройках браузера, но это может повлиять на функциональность Сервиса.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">8. Изменения в Политике</h2>
            <p>
              Оператор оставляет за собой право вносить изменения в настоящую Политику. 
              Актуальная версия всегда доступна на данной странице. Продолжение использования 
              Сервиса после внесения изменений означает согласие с новой редакцией Политики.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">9. Контактная информация</h2>
            <p>По всем вопросам, связанным с обработкой персональных данных, обращайтесь:</p>
            <ul className="list-none space-y-2">
              <li><strong>Оператор:</strong> Самозанятая Дмитренко Полина Андреевна</li>
              <li><strong>Telegram:</strong> <a href="https://t.me/momsclubsupport" className="text-[#B08968] hover:underline">@momsclubsupport</a></li>
              <li><strong>Email:</strong> support@momsclub.ru</li>
            </ul>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full px-6 py-6 border-t border-gray-200/50 mt-12">
        <div className="max-w-4xl mx-auto flex items-center justify-between text-sm text-gray-600">
          <p>© 2025 MomsClub. Все права защищены.</p>
          <div className="flex items-center space-x-6">
            <span className="text-[#B08968]">Политика</span>
            <Link href="/terms" className="hover:text-gray-900 transition-colors">Условия</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
