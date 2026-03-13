"""
MTK Chipset Database -- static lookup for device auto-detection.

Maps chipset names (as reported by mtkclient's chipconfig.name) to
marketing names, exploit engines, and support status.

Source: mtkclient project (https://github.com/bkerler/mtkclient)
"""

# ---------------------------------------------------------------
# Support status constants
# ---------------------------------------------------------------
SUPPORTED   = "SUPPORTED"       # Exploit works, full functionality
PARTIAL     = "PARTIAL"         # Exploit works but may be unreliable
AUTH_REQUIRED = "AUTH_REQUIRED"  # Patched BootROM, needs signed DA
UNKNOWN     = "UNKNOWN"         # Not in database

# ---------------------------------------------------------------
# Exploit engine constants
# ---------------------------------------------------------------
KAMAKIRI  = "kamakiri"
LINECODE  = "linecode"
PRELOADER = "preloader"
CARBONARA = "carbonara"

# ---------------------------------------------------------------
# Chipset database
# Key: chipset name (uppercase, e.g. "MT6765")
# mtkclient returns chipconfig.name in this format.
# ---------------------------------------------------------------
CHIPSET_DB = {
    # === Legacy MTK ===
    "MT6570": {
        "marketing": None,
        "family": "legacy",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6571": {
        "marketing": None,
        "family": "legacy",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6572": {
        "marketing": None,
        "family": "legacy",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6580": {
        "marketing": None,
        "family": "legacy",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6582": {
        "marketing": None,
        "family": "legacy",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6592": {
        "marketing": None,
        "family": "legacy",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6595": {
        "marketing": None,
        "family": "legacy",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },

    # === Mid generation ===
    "MT6735": {
        "marketing": None,
        "family": "mid",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6737": {
        "marketing": None,
        "family": "mid",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6739": {
        "marketing": None,
        "family": "mid",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6753": {
        "marketing": None,
        "family": "mid",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6755": {
        "marketing": "Helio P10",
        "family": "mid",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6757": {
        "marketing": "Helio P20 / P25",
        "family": "mid",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },

    # === Helio generation ===
    "MT6761": {
        "marketing": "Helio A22",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6762": {
        "marketing": "Helio P22",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6763": {
        "marketing": "Helio P23",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6765": {
        "marketing": "Helio P35 / G35",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6768": {
        "marketing": "Helio G80 / G85",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6769": {
        "marketing": "Helio P65 / G85",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6771": {
        "marketing": "Helio P60 / P70",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6779": {
        "marketing": "Helio G90",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6785": {
        "marketing": "Helio G90T / G95",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },
    "MT6797": {
        "marketing": "Helio X20 / X25",
        "family": "helio",
        "exploit": KAMAKIRI,
        "status": SUPPORTED,
    },

    # === Early Dimensity (partial support) ===
    "MT6833": {
        "marketing": "Dimensity 700",
        "family": "dimensity",
        "exploit": LINECODE,
        "status": PARTIAL,
    },
    "MT6853": {
        "marketing": "Dimensity 720",
        "family": "dimensity",
        "exploit": LINECODE,
        "status": PARTIAL,
    },
    "MT6873": {
        "marketing": "Dimensity 800",
        "family": "dimensity",
        "exploit": LINECODE,
        "status": PARTIAL,
    },
    "MT6875": {
        "marketing": "Dimensity 820",
        "family": "dimensity",
        "exploit": LINECODE,
        "status": PARTIAL,
    },
    "MT6877": {
        "marketing": "Dimensity 900",
        "family": "dimensity",
        "exploit": PRELOADER,
        "status": PARTIAL,
    },
    "MT6885": {
        "marketing": "Dimensity 1000",
        "family": "dimensity",
        "exploit": LINECODE,
        "status": PARTIAL,
    },

    # === New generation (patched BootROM -- auth required) ===
    "MT6781": {
        "marketing": "Helio G96",
        "family": "helio_new",
        "exploit": None,
        "status": AUTH_REQUIRED,
    },
    "MT6789": {
        "marketing": "Helio G99",
        "family": "helio_new",
        "exploit": None,
        "status": AUTH_REQUIRED,
    },
    "MT6891": {
        "marketing": "Dimensity 1100",
        "family": "dimensity_new",
        "exploit": None,
        "status": AUTH_REQUIRED,
    },
    "MT6893": {
        "marketing": "Dimensity 1200",
        "family": "dimensity_new",
        "exploit": None,
        "status": AUTH_REQUIRED,
    },
    "MT6895": {
        "marketing": "Dimensity 8100",
        "family": "dimensity_new",
        "exploit": None,
        "status": AUTH_REQUIRED,
    },
    "MT6983": {
        "marketing": "Dimensity 9000",
        "family": "dimensity_new",
        "exploit": None,
        "status": AUTH_REQUIRED,
    },
    "MT6985": {
        "marketing": "Dimensity 9200",
        "family": "dimensity_new",
        "exploit": None,
        "status": AUTH_REQUIRED,
    },
}


def lookup_chipset(chipname: str) -> dict:
    """Look up chipset info by name. Case-insensitive.

    Returns dict with keys: chipset, marketing, family, exploit, status.
    If not found, returns a dict with status=UNKNOWN.
    """
    if not chipname:
        return {
            "chipset": None,
            "marketing": None,
            "family": None,
            "exploit": None,
            "status": UNKNOWN,
        }

    # Normalize: strip whitespace, uppercase
    key = chipname.strip().upper()

    # Handle variants like "MT6768/MT6769" -- take first part
    if "/" in key:
        key = key.split("/")[0].strip()

    # Strip anything after a space or paren: "MT6768(Helio ...)" -> "MT6768"
    for sep in ("(", " "):
        if sep in key:
            key = key.split(sep)[0].strip()

    entry = CHIPSET_DB.get(key)

    if entry:
        return {
            "chipset": key,
            "marketing": entry["marketing"],
            "family": entry["family"],
            "exploit": entry["exploit"],
            "status": entry["status"],
        }

    return {
        "chipset": key,
        "marketing": None,
        "family": None,
        "exploit": None,
        "status": UNKNOWN,
    }


def get_support_status(chipname: str) -> str:
    """Return just the support status string for a chipset name."""
    return lookup_chipset(chipname)["status"]


def is_exploit_supported(chipname: str) -> bool:
    """Return True if chipset has a known working exploit."""
    status = get_support_status(chipname)
    return status in (SUPPORTED, PARTIAL)
