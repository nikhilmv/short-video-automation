# Next.js Admin Panel Starter

A minimal admin panel boilerplate: Next.js App Router + Tailwind CSS, with
login, signup, dashboard, and a user module (list + create).

## Stack
- Next.js 14 (App Router, JavaScript)
- Tailwind CSS — styled with reusable component classes (`.btn`, `.input`,
  `.card`, `.sidebar-link`, etc. defined in `app/globals.css`) so page
  markup stays short instead of long utility-class chains.
- Auth is mocked with `localStorage` (see `context/AuthContext.js`) so the
  app runs with zero backend setup. Swap it for real API calls when ready.

## Getting started
```bash
npm install
npm run dev
```
Visit http://localhost:3000 — you'll be redirected to `/login`.

**Demo account** (seeded automatically):
- Email: `admin@example.com`
- Password: `password123`

Or create a new account from the Sign up page.

## Structure
```
app/
  layout.js            root layout, wraps app in AuthProvider
  page.js              redirects to /dashboard or /login
  globals.css          Tailwind + all reusable component classes
  login/page.js
  signup/page.js
  dashboard/
    layout.js          protected shell (sidebar + topbar)
    page.js            dashboard with stat cards
  users/
    layout.js          protected shell
    page.js             user list (table)
    create/page.js      create user form
components/
  Sidebar.js, Topbar.js, ProtectedShell.js, FormField.js
context/
  AuthContext.js       mock login/signup/logout/addUser/listUsers
```

## Where to plug in a real backend
Replace the localStorage logic inside `context/AuthContext.js`
(`login`, `signup`, `addUser`, `listUsers`) with calls to your API
or auth provider (NextAuth, Clerk, your own REST/GraphQL API, etc.).
Every page in the app talks only to `useAuth()`, so the rest of the
app won't need to change.

## Customizing the theme
All colors, spacing, and component styles live in two places:
- `tailwind.config.js` — the `brand` color scale and a couple of tokens
- `app/globals.css` — component classes (`.btn-primary`, `.input`, `.card`, ...)

Change a color once in either file and it updates everywhere.
