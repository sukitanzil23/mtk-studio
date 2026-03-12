# MTK Studio -- Build Progress

| Phase | Description | Status | Agent | Notes |
|-------|-------------|--------|-------|-------|
| 1 | Project Scaffold | [x] done | CoderGPT + Coder | All files created |
| 2 | Static UI | [x] done | Coder | All UI pages created |
| 3 | Navigation + Routing | [x] done | Coder | SPA router, stepper, toast |
| 4 | Bridge Layer | [x] done | CoderGPT + Coder | api.py, mock.py, usb_monitor.py wired |
| 5 | FRP Bypass Wizard | [x] done | CoderGPT + Coder | Full 5-step wizard with callbacks |
| 6 | Device Detection + Footer | [x] done | CoderGPT + Coder | get_usb_status() wired with pyserial; USB monitor verified |
| 7 | Console / Log Panel | [ ] pending | Coder | |
| 8 | PyInstaller Packaging | [x] done | CoderGPT | build.spec.txt created with hiddenimports + datas |
| 9 | Git Push | [ ] pending | CoderGPT | |

## Blocked Issues
(none)

## Notes
- Mock mode: Settings > Mock Mode toggle
- Real device testing: deferred post-MVP
- mtkclient: add as git submodule in Phase 9
