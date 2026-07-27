# App Layout Design

## Overview
This document describes the layout for the Fooglemaps web application built with React. The layout follows common web application patterns with a header, navigation sidebar, and main content area.

## Layout Structure

### Header (Top Bar)
- **Position**: Fixed at top of viewport (z-50)
- **Height**: 60px (theme token `header`)
- **Contents**:
  - Hamburger button (toggles sidebar) on left
  - "Fooglemaps" logo/brand
  - Search bar (centered, hidden on mobile via `hidden md:block`)
  - UserMenu (avatar or sign-in button) on right
- **Behavior**: Remains visible on scroll

### Navigation Sidebar
- **Position**: Fixed left side, below header
- **Width**: 240px (theme token `sidebar`), collapsible to 60px icon-only mode (theme token `sidebar-sm`) via hamburger toggle
- **Contents**:
  - Navigation items:
    - Home (house icon)
    - Maps (map icon)
    - Search (magnifying glass icon)
    - Saved Places (bookmark icon)
    - Settings (cog icon)
  - Each item: icon + text label (icon-only when collapsed)
- **Behavior**:
  - Collapsible via hamburger button in header
  - Persistent across route changes
  - On mobile (<768px): renders as a drawer overlay with backdrop (controlled by `mobileOpen` state), triggered by hamburger

### Main Content Area
- **Position**: Fills remaining space (to right of sidebar, below header)
- **Padding**: Responsive (pt-16 for header, md:ml-60 or md:ml-16 depending on sidebar state)
- **Components**:
  - Page title/subtitle (via PageContainer)
  - Primary content (varies by route):
    - Home: Dashboard with Quick Actions cards + cuisine stats
    - Maps: Full-height Google Map with markers for food places
    - Search: Search form + cuisine/location filters
    - Saved: List of bookmarked food places with cuisine badges
    - Settings: Theme selector, map defaults, notification toggles

### Footer (Static)
- **Position**: Static after main content
- **Contents**: "© 2025 Fooglemaps · Privacy · Terms"
- **Visibility**: Visible on all pages

## Responsive Behavior

### Desktop (≥1024px)
- Sidebar expanded by default (collapsible via hamburger)
- Header fixed top
- Search bar visible

### Tablet (768px-1023px)
- Sidebar collapsible via hamburger
- Search bar visible

### Mobile (<768px)
- Sidebar converts to drawer overlay with backdrop
- Search bar hidden (`hidden md:block`)
- Main content uses full viewport width
- Hamburger opens sidebar as overlay

## Component Breakdown

### Reusable Components
1. **AppHeader**: Hamburger, logo, search, UserMenu
2. **NavSidebar**: Collapsible navigation with NavLink active states and SVG icons
3. **MainLayout**: Wrapper that positions header, sidebar, `<Outlet />`, and Footer
4. **PageContainer**: Title + optional subtitle + children wrapper
5. **UserMenu**: Avatar button with dropdown — shows "Sign in" (unauthenticated) or Saved/Settings/Sign out (authenticated)
6. **Footer**: Static copyright + Privacy/Terms links

### Route-Specific Components
- **HomePage**: Dashboard widgets (Quick Actions) + food spot count + cuisine tags
- **MapsPage**: Google Map with `AdvancedMarkerElement` markers + `InfoWindow` on click
- **SearchPage**: Search input + cuisine/location dropdowns + Search button
- **SavedPage**: List of saved places with cuisine badges and bookmark button
- **SettingsPage**: Theme selector (light/dark/system), default zoom, map type, notification toggles
- **SignInPage**: Full-screen centered Google Sign-In button

## State Management
- **AuthContext**: `user`, `settings`, `loading`, `signIn()`, `signOut()`, `updateSettings()` — persists token in `sessionStorage`
- **SidebarContext**: `collapsed` (desktop toggle), `mobileOpen` (mobile drawer), `isMobile` (breakpoint detection)
- **ThemeContext**: `preference` (light/dark/system), resolved theme, `data-theme` attribute on `<html>`, persists to `localStorage`

## Styling Approach
- **Tailwind CSS** for utility-first styling
- **CSS custom properties** defined in `src/index.css` for light/dark theme variables
- **Tailwind config** extended with custom colors (`primary`, `surface`, `content`, `border`, `sidebar`, `header`, `card`) and spacing (`header`, `sidebar`, `sidebar-sm`, `footer`) from `src/themes/*`
- **Dark mode** via `data-theme` selector (Tailwind `darkMode: 'selector'`)
- **CSS variables** toggled via `[data-theme="dark"]` and `[data-theme="light"]` selectors

## Performance Considerations
- Map component uses `useEffect` cleanup to prevent memory leaks
- `AuthContext` skips token verification on mount if no token is in `sessionStorage`

## Implementation Notes
- Uses React Router v7 for routing (`react-router-dom`)
- Header remains mounted across route changes (part of `MainLayout`)
- Sidebar state managed via React Context API
- Google Maps loaded via `import { Loader } from '@googlemaps/js-api-loader'`
- Google Identity Services (GIS) for OAuth
