# PIYASH LEVEL UP Management Panel

A high-performance management dashboard for orchestrating concurrent game automation sessions across two distinct categories: **2 Level** (Standby, Chat, Room, and Team management) and **3 Level** (Continuous Lone Wolf matchmaking auto-pump).

---

## User Review & Critical Decisions

> [!IMPORTANT]
> Both categories require dedicated "Create a New Account" interfaces and isolated concurrent execution. Based on the analysis of both Python scripts:
> - **2 Level**: Implements standard connection lifecycle (Update → MajorLogin → GetLoginData → dual TCP chat & online sockets with invite and chat authorization).
> - **3 Level**: Implements continuous Lone Wolf match-pump injection (`lobby_clear_packet` + `match_start_packet` every 5.7s) running parallel with dynamic UDP session handlers.
>
> All accounts are persisted locally in a Room database with multi-instance concurrency isolation so starting or stopping one account never affects another.

---

## 1. Overview & Core Concept

**PIYASH LEVEL UP** provides a tactical management panel to configure, launch, monitor, and terminate multiple game sessions simultaneously.

### Key Value
- **Dual Category Segmentation**: Distinct workspaces for **2 Level** and **3 Level** with dedicated creation forms, status trackers, and execution pipelines.
- **Process & Session Isolation**: Prevents memory or socket state collisions between accounts so that dozens of instances can run concurrently.
- **Real-Time Telemetry & Logs**: Live inspection of packet handshakes (TCP/UDP, Auth, Room, Matchmaking) with colored event tags.

---

## 2. User Experience & Visual Design

### Aesthetic Direction
- **Cyber-Tactical Dark Gaming UI**: Deep obsidian `#0B0F19` and midnight blue `#111827` backdrops, neon emerald `#10B981` (2 Level) and electric cyan/purple `#6366F1` (3 Level) accents.
- **Typography & Hierarchy**: Bold monospace font for UIDs and timestamps, crisp sans-serif for labels and status indicators.

### Key User Flows

```
┌────────────────────────────────────────────────────────┐
│                   PIYASH LEVEL UP                      │
│        [ 2 Level (Active: 3) ]   [ 3 Level (Active: 2) ]│
└────────────────────────────────────────────────────────┘
                           │
       ┌───────────────────┴───────────────────┐
       ▼                                       ▼
┌───────────────────────────┐     ┌───────────────────────────┐
│     + Create Account      │     │      Accounts List        │
│ ┌───────────────────────┐ │     │ ┌───────────────────────┐ │
│ │ UID: [ 794006       ] │ │     │ │ Bot Alpha (2 Level)   │ │
│ │ PASS: [ ••••••••    ] │ │     │ │ Status: [ Online ]    │ │
│ │ Name: [ M4RUF Bot   ] │ │     │ │ [ Stop ] [ View Logs] │ │
│ │ [ Cancel ] [ Start ]  │ │     │ └───────────────────────┘ │
│ └───────────────────────┘ │     │ ┌───────────────────────┐ │
│                           │     │ │ Bot Beta (3 Level)    │ │
│                           │     │ │ Status: [ In-Match ]  │ │
│                           │     │ │ [ Stop ] [ View Logs] │ │
│                           │     │ └───────────────────────┘ │
└───────────────────────────┘     └───────────────────────────┘
```

1. **Dashboard & Category Selection**:
   - Top segmented tabs switch between **2 Level** and **3 Level**.
   - Category-specific statistics: total accounts, active sessions, and match counters.
2. **"Create a New Account" Modal / BottomSheet**:
   - Input fields: **UID** (number validation), **Password** (secure toggle), and **Custom Name**.
   - Action controls: **Start** (validates inputs, persists account, starts session immediately) and **Cancel** (dismisses form).
3. **Account Cards**:
   - Badge showing category tag (`2 LEVEL` or `3 LEVEL PUMP`).
   - Real-time status indicators: `Idle`, `Authenticating`, `Connected (TCP)`, `Pumping Queue`, `In Match (UDP)`, `Stopped`, `Crashed`.
   - Control buttons: Quick **Start / Stop** toggle with safety confirmation.
   - **Live Logs Sheet**: Terminal-style expandable log viewer showing live protocol events and timestamps.

---

## 3. Key Product Decisions & Trade-Offs

- **Architecture Strategy: Modular Kotlin Protocol Engine vs Subprocesses**:
  - *Decision*: Build native Kotlin asynchronous session managers (`BotSession`) replicating the packet builders, AES/TEA/CRC7 encryptions, and TCP/UDP sockets directly inside Android with coroutines.
  - *Why*: Delivers lightning-fast startup, battery-efficient background coroutines, eliminates heavy Python runtime overhead on mobile devices, and provides seamless reactive UI integration.
- **Concurrency Isolation**:
  - *Decision*: Encapsulate all connection variables (`chatWriter`, `onlineWriter`, `jwtToken`, `accountId`, `pumpJob`) inside discrete `BotSession` instances.
  - *Why*: Completely solves the global variable collision flaw found in the original Python scripts.
- **Local Persistence via Room**:
  - *Decision*: Store all configured accounts, credentials, and last-known status in SQLite via Room.
  - *Why*: Instant offline access, survives app restarts, and provides reactive `Flow` updates to Compose UI.

---

## 4. Technical Architecture & Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      UI Layer (Compose)                      │
│   DashboardScreen ── CategoryTabs ── CreateAccountDialog    │
│   AccountCardGrid ── LiveLogSheet  ── StatusBadges          │
└──────────────────────────────┬───────────────────────────────┘
                               │ Observes StateFlow / Actions
┌──────────────────────────────▼───────────────────────────────┐
│                    ViewModel (PanelViewModel)                │
│    AccountsState, ActiveSessionsMap, LogStreams, Stats       │
└──────────────┬───────────────────────────────┬───────────────┘
               │                               │
┌──────────────▼──────────────┐ ┌──────────────▼───────────────┐
│     AccountRepository       │ │      SessionCoordinator      │
│  (Room AppDatabase & DAO)   │ │  Manages Concurrent Sessions │
│  - BotAccountEntity         │ └──────────────┬───────────────┘
│  - Persistent Logs Table    │                │ Spawns isolated
└─────────────────────────────┘ ┌──────────────▼───────────────┐
                                │          BotSession          │
                                │  ├── Level2Handler (Standby) │
                                │  └── Level3Handler (AutoPump)│
                                │  ├── REST OAuth Client       │
                                │  ├── Dual TCP Sockets        │
                                │  └── Async UDP State Machine │
                                └──────────────────────────────┘
```

### Data Model (`BotAccountEntity`)
- `id: Long` (Primary Key auto-generated)
- `category: String` ("LEVEL_2" or "LEVEL_3")
- `uid: Long`
- `password: String`
- `customName: String`
- `status: String` ("IDLE", "CONNECTING", "ONLINE", "IN_MATCH", "STOPPED", "ERROR")
- `lastActiveTimestamp: Long`
- `matchCount: Int`

### Execution Pipelines:
- **Level 2 Handler**: Executes OAuth guest grant → MajorLogin → GetLoginData → dual TCP sockets (`tcp_chat` + `tcp_online`) → standby invite/friend handling.
- **Level 3 Handler**: Executes identical login sequence + launches `MatchmakingPump` coroutine sending 0319 lobby clear and 0319 Lone Wolf queue packets every 5.7s, dispatching independent UDP game handlers upon match discovery.

---

## 5. Verification Plan

1. **Compilation**: Run `compile_applet` to ensure Room, KSP, and Jetpack Compose configurations build cleanly.
2. **Account Creation Validation**: Create separate accounts under both "2 Level" and "3 Level" with validation on UID and Password fields.
3. **Session Lifecycle**: Verify independent Start, Stop, and Status updates for multiple accounts simultaneously without cross-talk or UI blocking.
4. **Log Inspection**: Verify logs are segregated per account and display real-time network states.
