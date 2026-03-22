# Simulation shell for POTASSIUM-WORKSHOP
#
# Provides a Python 3.10 environment pinned to the same nixpkgs commit used by
# artiq/flake.nix (nixos-22.11), so llvmlite and other deps are compatible with
# artiq 8.  Local lab repos are added to PYTHONPATH rather than built as Nix
# packages, which avoids versioneer / GUI-dep complications.
#
# Pure-Python PyPI deps (sympy, lmfit, asteval, uncertainties) are fetched as
# pre-built wheels (format = "wheel") so setup.py never runs and setup_requires
# like setuptools_scm / future never trigger the network in the Nix sandbox.
#
# arc-alkali-rydberg-calculator has a C extension and no Linux wheel, so it is
# built from the sdist.  Its only setup_requires ("oldest-supported-numpy") is
# patched out via substituteInPlace; numpy is already present as a build dep.
#
# Usage:
#   nix-shell                          # enter the shell
#   artiq-run --device-db sim/device_db.py \
#     k-exp/kexp/experiments/test/raman_pulse_test.py

let
  nixpkgs = builtins.fetchGit {
    url = "https://github.com/NixOS/nixpkgs";
    rev = "54644f409ab471e87014bb305eac8c50190bcf48"; # nixos-22.11
  };

  pkgs = import nixpkgs {};
  py  = pkgs.python3Packages;

  # ── sipyco (pinned to artiq's flake.lock) ───────────────────────────────
  sipyco = py.buildPythonPackage {
    pname = "sipyco";
    version = "1.4";
    src = builtins.fetchGit {
      url = "https://github.com/m-labs/sipyco";
      rev = "38f8f4185d7db6b68bd7f71546da9077b1e2561c";
    };
    propagatedBuildInputs = [ py.numpy ];
    doCheck = false;
  };

  # ── pythonparser (pinned to artiq's flake.lock) ─────────────────────────
  pythonparser = py.buildPythonPackage {
    pname = "pythonparser";
    version = "1.4";
    src = builtins.fetchGit {
      url = "https://github.com/m-labs/pythonparser";
      rev = "5413ee5c9f8760e95c6acd5d6e88dabb831ad201";
    };
    propagatedBuildInputs = [ py.regex ];
    doCheck = false;
  };

  # ── sympy 1.11.1 — wheel, no setup.py ───────────────────────────────────
  sympy = py.buildPythonPackage {
    pname = "sympy";
    version = "1.11.1";
    format = "wheel";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/2d/49/a2d03101e2d28ad528968144831d506344418ef1cc04839acdbe185889c2/sympy-1.11.1-py3-none-any.whl";
      sha256 = "938f984ee2b1e8eae8a07b884c8b7a1146010040fccddc6539c54f401c8f6fcf";
    };
    propagatedBuildInputs = [ py.mpmath ];
    doCheck = false;
  };

  # ── asteval 0.9.28 — wheel, avoids setuptools_scm setup_requires ─────────
  asteval = py.buildPythonPackage {
    pname = "asteval";
    version = "0.9.28";
    format = "wheel";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/dd/05/c28af7a26e90a1b1ec10bb7b451a30f745494941d5470131e0ffee075c33/asteval-0.9.28-py3-none-any.whl";
      sha256 = "c263d25bcc76d5fbeae68b7954b6f7bb16067232b515e4da01e3653e2ec01341";
    };
    doCheck = false;
  };

  # ── uncertainties 3.1.7 — wheel, avoids future install_requires ──────────
  # future is an unconditional runtime Requires-Dist of this version
  # (used for Py2/3 compat shims); py.future is in nixpkgs-22.11.
  uncertainties = py.buildPythonPackage {
    pname = "uncertainties";
    version = "3.1.7";
    format = "wheel";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/13/f7/9d94eeea3f6475456fb5c6b72d3a3cc652c1ecd342c5491274cbfc9ebaab/uncertainties-3.1.7-py2.py3-none-any.whl";
      sha256 = "4040ec64d298215531922a68fa1506dc6b1cb86cd7cca8eca848fcfe0f987151";
    };
    propagatedBuildInputs = [ py.numpy py.future ];
    doCheck = false;
  };

  # ── lmfit 1.1.0 — wheel, no setup.py ────────────────────────────────────
  lmfit = py.buildPythonPackage {
    pname = "lmfit";
    version = "1.1.0";
    format = "wheel";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/ea/ab/87059c989f262c88821cdc960944f0830e241c240652eef55e3eb8508e46/lmfit-1.1.0-py3-none-any.whl";
      sha256 = "29f0540f94b3969a23db2b51abf309f327af8ea3667443ac4cd93d07fdfdb14f";
    };
    propagatedBuildInputs = [ py.numpy py.scipy sympy asteval uncertainties py.matplotlib ];
    doCheck = false;
  };

  # ── arc-alkali-rydberg-calculator 3.4.1 ─────────────────────────────────
  # Has a C extension; no Linux wheel on PyPI — must build from sdist.
  # Patches out setup_requires = ["oldest-supported-numpy"]; numpy is already
  # present as a nativeBuildInput so the C extension compiles fine.
  arc = py.buildPythonPackage {
    pname = "arc-alkali-rydberg-calculator";
    version = "3.4.1";
    format = "setuptools";
    src = pkgs.fetchurl {
      url = "https://files.pythonhosted.org/packages/35/91/ab23e869a8fbe8661e07e9728e650a6e312fc76c23367ebcddb84d8cf1dd/ARC-Alkali-Rydberg-Calculator-3.4.1.tar.gz";
      sha256 = "dee81a906ad6159ebb4926a8339ef3179869646086f3b818bb68462c924c6c50";
    };
    nativeBuildInputs = [ py.numpy ];
    preBuild = ''
      substituteInPlace setup.py \
        --replace 'setup_requires=["oldest-supported-numpy"]' 'setup_requires=[]'
    '';
    propagatedBuildInputs = [ py.numpy py.scipy sympy lmfit py.matplotlib ];
    doCheck = false;
  };

  # ── Combined Python environment ──────────────────────────────────────────
  # artiq, waxx, waxa, kexp are loaded via PYTHONPATH from local clones
  # (avoids versioneer and GUI-dep complications at build time).
  pythonEnv = pkgs.python3.withPackages (ps: [
    sipyco
    pythonparser
    arc           # real ARC physics — sympy, lmfit, uncertainties, asteval pulled in
    ps.llvmlite   # must match artiq 8 / LLVM 11; nixpkgs-22.11 provides 0.39.x
    ps.numpy
    ps.scipy
    ps.h5py
    ps.pandas
    ps.matplotlib
    ps.pyserial
    ps.prettytable
    ps.python-dateutil
    ps.levenshtein
    ps.opencv4
    ps.lmdb
    ps.pint
  ]);

in pkgs.mkShell {
  buildInputs = [ pythonEnv ];

  shellHook = ''
    WORKSPACE="$(pwd)"

    # ── PYTHONPATH ────────────────────────────────────────────────────────
    # NIX_SITE is set by Nix interpolation at eval time to the exact store
    # path of the pythonEnv site-packages directory.  This makes h5py,
    # numpy, etc. importable without relying on wrapper-script or
    # sitecustomize.py ordering, which is fragile when our own
    # sitecustomize.py is first on sys.path.
    #
    # Ordering rules:
    #   arc     — Nix-installed; appears in NIX_SITE, never shadowed by stubs
    #   k-amo   — before sim/stubs so real kamo physics always wins
    #   sim/stubs — before pyLabLib so camera-SDK stubs win over real Andor/pypylon
    NIX_SITE="${pythonEnv}/${pkgs.python3.sitePackages}"
    export PYTHONPATH="$WORKSPACE:$WORKSPACE/artiq:$WORKSPACE/wax/waxx-src:$WORKSPACE/wax/waxa-src:$WORKSPACE/k-exp:$WORKSPACE/k-amo:$WORKSPACE/sim/stubs:$WORKSPACE/pyLabLib:$NIX_SITE"

    # ── Environment variables expected by kexp/config/ip.py ───────────────
    export data="$WORKSPACE/sim-data"
    export code="$WORKSPACE"

    # ── Create sim-data directory and run_id file ─────────────────────────
    mkdir -p "$WORKSPACE/sim-data"
    mkdir -p "$WORKSPACE/sim-data/logs"
    if [ ! -f "$WORKSPACE/sim-data/run_id.py" ]; then
      echo "1" > "$WORKSPACE/sim-data/run_id.py"
    fi
    if [ ! -f "$WORKSPACE/sim-data/device_state_config.json" ]; then
      echo '{"dds": {}, "dac": {}, "ttl": {}}' > "$WORKSPACE/sim-data/device_state_config.json"
    fi

    # ── artiq_run wrapper (artiq is on PYTHONPATH, not installed as cmd) ──
    artiq-run() {
      python3 -m artiq.frontend.artiq_run "$@"
    }
    export -f artiq-run

    echo ""
    echo "┌─ POTASSIUM-WORKSHOP simulation shell ──────────────────────────┐"
    printf "│  Python: %-54s│\n" "$(python3 --version 2>&1)"
    printf "│  arc:    %-54s│\n" "$(python3 -c 'import arc; print(arc.__version__)' 2>/dev/null || echo 'not loaded')"
    printf "│  data:   %-54s│\n" "$data"
    printf "│  code:   %-54s│\n" "$code"
    echo "│                                                                 │"
    echo "│  Run an experiment:                                             │"
    echo "│    artiq-run --device-db sim/device_db.py \\                   │"
    echo "│      k-exp/kexp/experiments/test/raman_pulse_test.py           │"
    echo "└─────────────────────────────────────────────────────────────────┘"
    echo ""
  '';
}
