'use client'

import Link from 'next/link'

export default function TermsPage() {
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
        <h1 className="text-3xl font-bold text-[#2D2A26] mb-8">Условия использования</h1>
        
        <div className="prose prose-lg max-w-none text-[#5C5650] space-y-6">
          <p className="text-sm text-[#8B8279]">Дата последнего обновления: 1 декабря 2025 года</p>
          
          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">1. Общие положения</h2>
            <p>
              Настоящие Условия использования (далее — «Условия») регулируют отношения между 
              Самозанятая Дмитренко Полина Андреевна (далее — «Исполнитель») и пользователем сервиса 
              LibriMomsClub (далее — «Сервис», «Библиотека»).
            </p>
            <p>
              Используя Сервис, вы подтверждаете, что ознакомились с настоящими Условиями, 
              Политикой конфиденциальности и принимаете их в полном объёме.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">2. Описание Сервиса</h2>
            <p>
              LibriMomsClub — это закрытая онлайн-библиотека контента для блогеров-мам, 
              предоставляющая доступ к:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Идеям для Reels и публикаций</li>
              <li>Гайдам по ведению блога</li>
              <li>Стратегиям продвижения</li>
              <li>Шаблонам и примерам контента</li>
              <li>Обучающим материалам</li>
            </ul>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">3. Условия доступа</h2>
            <p>
              Доступ к Библиотеке предоставляется пользователям с активной подпиской Mom&apos;s Club. 
              Авторизация осуществляется через Telegram-аккаунт.
            </p>
            <p>
              Подписка оформляется через Telegram-бот 
              <a href="https://t.me/momsclubsubscribe_bot" className="text-[#B08968] hover:underline ml-1">@momsclubsubscribe_bot</a>.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">4. Стоимость и оплата</h2>
            <p>Актуальные тарифы подписки:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li><strong>1 месяц</strong> — 990 ₽</li>
              <li><strong>2 месяца</strong> — 1 790 ₽ (экономия 190 ₽)</li>
              <li><strong>3 месяца</strong> — 2 490 ₽ (экономия 480 ₽)</li>
            </ul>
            <p>
              Оплата производится через платёжную систему ЮKassa. Все платежи защищены 
              и соответствуют требованиям PCI DSS.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">5. Автопродление</h2>
            <p>
              При оформлении подписки может быть включено автопродление. Вы можете отключить 
              автопродление в любой момент через личный кабинет в Telegram-боте. Отключение 
              автопродления не влияет на текущий оплаченный период.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">6. Возврат средств</h2>
            <p>
              Возврат денежных средств возможен в течение 3 дней с момента оплаты, если вы 
              не воспользовались материалами Библиотеки. Для оформления возврата обратитесь 
              в поддержку: <a href="https://t.me/momsclubsupport" className="text-[#B08968] hover:underline">@momsclubsupport</a>.
            </p>
            <p>
              После истечения 3 дней или при использовании материалов возврат не производится.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">7. Права на контент</h2>
            <p>
              Все материалы Библиотеки являются интеллектуальной собственностью Исполнителя 
              и защищены законодательством об авторском праве.
            </p>
            <p><strong>Запрещается:</strong></p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Копирование и распространение материалов третьим лицам</li>
              <li>Передача доступа к аккаунту другим лицам</li>
              <li>Использование материалов в коммерческих целях без согласования</li>
              <li>Публикация материалов без изменений как собственного контента</li>
            </ul>
            <p>
              <strong>Разрешается:</strong> использовать идеи и концепции для создания 
              собственного уникального контента.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">8. Ответственность</h2>
            <p>
              Исполнитель не несёт ответственности за результаты применения материалов 
              Библиотеки, так как успех блога зависит от множества факторов.
            </p>
            <p>
              Исполнитель обязуется обеспечить доступ к Сервису 24/7, за исключением 
              плановых технических работ и форс-мажорных обстоятельств.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">9. Блокировка доступа</h2>
            <p>Исполнитель оставляет за собой право заблокировать доступ пользователя при:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Нарушении настоящих Условий</li>
              <li>Распространении материалов третьим лицам</li>
              <li>Попытках взлома или нарушения работы Сервиса</li>
              <li>Оскорбительном поведении в отношении других пользователей или команды</li>
            </ul>
            <p>При блокировке за нарушения возврат средств не производится.</p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">10. Реферальная программа</h2>
            <p>
              Пользователи могут участвовать в реферальной программе и получать бонусы за 
              приглашённых друзей. Условия реферальной программы могут изменяться, актуальная 
              информация доступна в Telegram-боте.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">11. Изменение Условий</h2>
            <p>
              Исполнитель вправе изменять настоящие Условия. Уведомление об изменениях 
              публикуется на данной странице. Продолжение использования Сервиса после 
              изменений означает согласие с новой редакцией.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">12. Применимое право</h2>
            <p>
              Настоящие Условия регулируются законодательством Российской Федерации. 
              Все споры разрешаются путём переговоров, а при невозможности достижения 
              согласия — в суде по месту нахождения Исполнителя.
            </p>
          </section>

          <section className="space-y-4">
            <h2 className="text-xl font-semibold text-[#2D2A26]">13. Контакты</h2>
            <p>По всем вопросам обращайтесь:</p>
            <ul className="list-none space-y-2">
              <li><strong>Исполнитель:</strong> Самозанятая Дмитренко Полина Андреевна</li>
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
            <Link href="/privacy" className="hover:text-gray-900 transition-colors">Политика</Link>
            <span className="text-[#B08968]">Условия</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
