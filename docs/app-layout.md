# App Layout Design

## Overview
This document describes the proposed layout for the Fooglemaps web application built with JavaScript/React. The layout follows common web application patterns with a header, navigation sidebar, and main content area.

## Layout Structure

### Header (Top Bar)
- **Position**: Fixed at top of viewport
- **Height**: 60px
- **Contents**:
  - Application logo/brand on left
  - Search bar (prominent, centered)
  - User avatar/notifications/profile menu on right
- **Behavior**: Remains visible on scroll; may shrink on scroll down for more vertical space

### Navigation Sidebar
- **Position**: Fixed left side, below header
- **Width**: 240px (collapsible to 60px icon-only mode)
- **Contents**:
  - Brand/logo (optional duplicate)
  - Navigation items:
    - Dashboard/Home
    - Maps
    - Search
    - Saved Places
    - Routes
    - Settings
  - Each item: icon + text label (icon-only when collapsed)
- **Behavior**: 
  - Collapsible via hamburger/menu button in header
  - Persistent across route changes
  - Scrollable if content exceeds viewport height

### Main Content Area
- **Position**: Fill remaining space (to right of sidebar, below header)
- **Padding**: 24px responsive padding
- **Components**:
  - Page title/breadcrumb bar
  - Primary content (varies by route):
    - Home: Welcome message, quick actions, recent activity
    - Maps: Map container with controls (zoom, layers, search)
    - Search: Search form + results list/map
    - Saved: Grid/list of saved places/folders
    - Settings: Form sections

### Footer (Optional)
- **Position**: Fixed at bottom or static after main content
- **Contents**: Copyright, links to terms/privacy, version number
- **Visibility**: May be hidden on auth pages or full-screen modals

## Responsive Behavior

### Desktop (≥1024px)
- Sidebar expanded by default
- Header fixed top
- Main content uses grid/flex layout

### Tablet (768px-1023px)
- Sidebar may start collapsed (icon-only) or be toggleable
- Header elements may adjust (search bar may move to sidebar)
- Main content uses full width minus sidebar

### Mobile (<768px)
- Sidebar converted to bottom navigation bar (as originally considered) OR drawer menu
- Header height reduced
- Main content uses full viewport width
- Bottom navigation options: Home, Maps, Search, Saved, Profile (if using bottom nav)
- OR: Hamburger menu opens sidebar as drawer overlay

## Component Breakdown

### Reusable Components
1. **AppHeader**: Logo, search, user menu
2. **NavSidebar**: Collapsible navigation with active state indicators
3. **MainLayout**: Wrapper that positions header, sidebar, main content
4. **PageContainer**: Contains page title, breadcrumbs, and children
5. **MapContainer**: Leaflet/Google Maps wrapper with controls
6. **SearchBar**: Debounced input with suggestions
7. **UserMenu**: Avatar, dropdown with profile, settings, logout
8. **Footer**: Optional static/footer component

### Route- Specific Components
- **HomePage**: Dashboard widgets, quick actions
- **MapsPage**: MapContainer + layers panel + place search sidebar
- **SearchPage**: SearchForm + ResultsList + ResultsMap
- **SavedPage**: Folder list + Items grid/list
- **SettingsPage**: Form sections with save/cancel

## State Management Considerations
- User auth state (global)
- Sidebar collapsed state (global or context)
- Selected route/location (may be URL-sync)
- Map state (bounds, zoom, layers) - consider keeping in URL or app state
- Search query and results

## Styling Approach
- Use CSS modules or styled-components for scoping
- Follow consistent spacing (8px grid)
- Utilize CSS variables for theme colors (primary, secondary, background, text)
- Ensure accessibility: proper ARIA labels, keyboard navigation, focus management
- Dark/light theme support via CSS variables

## Performance Considerations
- Lazy load route-specific components via React.lazy
- Virtualize long lists (saved places, search results)
- Debounce search inputs
- Memoize expensive calculations
- Consider server-side rendering for initial load if SEO needed

## Implementation Notes
- Use React Router v6 for navigation
- Header remains mounted across route changes
- Sidebar state managed via Context API or state management library (Redux/Zustand)
- Map library integration: ensure proper cleanup on unmount
- Consider using React Query/SWR for data fetching
- Form validation with React Hook Form or similar