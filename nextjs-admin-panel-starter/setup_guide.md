# Next.js Admin Panel Setup Guide

This document outlines the steps to build the front end from scratch, replicating the setup of the `nextjs-admin-panel-starter` project. The project utilizes **Next.js 14**, **React 18**, and **Tailwind CSS**.

## Prerequisites
Make sure you have Node.js installed on your system. You can verify this by running:
```bash
node -v
npm -v
```

## Step 1: Create a new Next.js Project

The easiest way to set up a new Next.js project is using `create-next-app`. Open your terminal and run the following command in the directory where you want your new project:

```bash
npx create-next-app@14.2.35 nextjs-admin-panel-starter
```

During the setup process, you will be prompted with a few questions. To match your current project, answer them as follows:

- Would you like to use TypeScript? **No**
- Would you like to use ESLint? **Yes**
- Would you like to use Tailwind CSS? **Yes**
- Would you like to use `src/` directory? **No** (Since your current app uses the root `app/` directory)
- Would you like to use App Router? (recommended) **Yes**
- Would you like to customize the default import alias? **No**

## Step 2: Navigate to the Project Directory

Once the installation is complete, navigate into the newly created project folder:

```bash
cd nextjs-admin-panel-starter
```

## Step 3: Verify Dependencies

Your `package.json` should now look very similar to your current setup. The command above automatically installed the necessary dependencies:
- `next`
- `react`
- `react-dom`
- `tailwindcss`
- `postcss`
- `autoprefixer`

## Step 4: Project Structure Setup

Based on your current workspace, you should manually recreate the folders and files that you need. Run these commands or manually create the folders:

```bash
# Create the components folder
mkdir components

# Create the specific page folders inside the app directory
mkdir app/dashboard
mkdir app/login
mkdir app/signup
```

### Create Boilerplate Files

You can then create the files you were working on. For instance:

**1. Form Component**
Create a new file `components/FormField.js`.

**2. Dashboard Layout**
Create `app/dashboard/layout.js`.

**3. Login & Signup Pages**
Create `app/login/page.js` and `app/signup/page.js`.

## Step 5: Start the Development Server

To see your app in action, start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result. You can now start building out the UI components and pages using Tailwind CSS and Next.js App Router!
