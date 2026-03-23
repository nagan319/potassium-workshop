{
  description = ''
    POTASSIUM-WORKSHOP — ARTIQ simulation environment for cold-K experiments at UCSB.

    Provides a Python 3.10 environment with:
      - ARTIQ 8 (release-8-ucsb branch) on PYTHONPATH
      - waxx/waxa, k-exp, k-amo lab packages on PYTHONPATH
      - All physics deps (ARC, pint, lmfit, sympy, …) as real packages
      - Hardware SDK stubs (spcm, pypylon, PyQt6, vxi11, …) via sim/stubs/

    Lab repos (artiq/, k-exp/, wax/, k-amo/, spcm/, pyLabLib/) are NOT part of
    this flake — clone them first with:  ./manage_lab.sh

    Usage:
      nix develop          # enter dev shell  (flakes enabled)
      nix-shell            # enter dev shell  (classic, uses shell.nix)
  '';

  inputs = {
    # Pinned to the same nixos-22.11 commit as shell.nix so llvmlite 0.39.x
    # (compatible with ARTIQ 8 / LLVM 11) is available.
    nixpkgs.url = "github:NixOS/nixpkgs/54644f409ab471e87014bb305eac8c50190bcf48";

    # Pinned to artiq's flake.lock commits — must stay in sync with the artiq
    # submodule in this workspace.
    sipyco-src = {
      url = "github:m-labs/sipyco/38f8f4185d7db6b68bd7f71546da9077b1e2561c";
      flake = false;
    };
    pythonparser-src = {
      url = "github:m-labs/pythonparser/5413ee5c9f8760e95c6acd5d6e88dabb831ad201";
      flake = false;
    };
  };

  outputs = { self, nixpkgs, sipyco-src, pythonparser-src }:
  let
    # Only x86_64-linux is supported. llvmlite 0.39.x (required by ARTIQ 8)
    # is not available for aarch64-darwin in nixpkgs-22.11.  macOS support
    # would require a different nixpkgs pin or a custom LLVM overlay.
    system = "x86_64-linux";
    pkgs   = import nixpkgs { inherit system; };
    py     = pkgs.python3Packages;

    # ── sipyco ────────────────────────────────────────────────────────────────
    sipyco = py.buildPythonPackage {
      pname = "sipyco";
      version = "1.4";
      src = sipyco-src;
      propagatedBuildInputs = [ py.numpy ];
      doCheck = false;
    };

    # ── pythonparser ──────────────────────────────────────────────────────────
    pythonparser = py.buildPythonPackage {
      pname = "pythonparser";
      version = "1.4";
      src = pythonparser-src;
      propagatedBuildInputs = [ py.regex ];
      doCheck = false;
    };

    # ── sympy 1.11.1 — wheel ─────────────────────────────────────────────────
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

    # ── asteval 0.9.28 — wheel ────────────────────────────────────────────────
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

    # ── uncertainties 3.1.7 — wheel ──────────────────────────────────────────
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

    # ── lmfit 1.1.0 — wheel ───────────────────────────────────────────────────
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

    # ── arc-alkali-rydberg-calculator 3.4.1 — sdist (has C extension) ────────
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

    # ── Combined Python environment ────────────────────────────────────────────
    # artiq, waxx, waxa, k-exp, k-amo are loaded via PYTHONPATH from local
    # clones (avoids versioneer and GUI-dep complications at Nix build time).
    pythonEnv = pkgs.python3.withPackages (ps: [
      sipyco
      pythonparser
      arc
      ps.llvmlite    # 0.39.x from nixpkgs-22.11, compatible with ARTIQ 8 / LLVM 11
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

    # ── Container entrypoint ──────────────────────────────────────────────────
    # Sets up PYTHONPATH so that the container works identically to nix-shell.
    # The lab repos (artiq/, k-exp/, etc.) are expected at /workspace, mounted
    # at runtime via -v $(pwd):/workspace (Docker) or --bind (Apptainer).
    # NIX_SITE is baked in at image-build time as a fixed Nix store path.
    containerEntrypoint = pkgs.writeScript "potassium-entrypoint" ''
      #!${pkgs.bash}/bin/bash
      WORKSPACE="''${WORKSPACE:-/workspace}"
      NIX_SITE="${pythonEnv}/${pkgs.python3.sitePackages}"
      export PYTHONPATH="$WORKSPACE/sim/stubs:$WORKSPACE:$WORKSPACE/artiq:$WORKSPACE/wax/waxx-src:$WORKSPACE/wax/waxa-src:$WORKSPACE/k-exp:$WORKSPACE/k-amo:$WORKSPACE/pyLabLib:$NIX_SITE"
      export data="$WORKSPACE/sim-data"
      export code="$WORKSPACE"
      mkdir -p "$WORKSPACE/sim-data/logs"
      [ -f "$WORKSPACE/sim-data/run_id.py" ] || echo "1" > "$WORKSPACE/sim-data/run_id.py"
      [ -f "$WORKSPACE/sim-data/device_state_config.json" ] || \
        echo '{"dds":{},"dac":{},"ttl":{}}' > "$WORKSPACE/sim-data/device_state_config.json"
      exec "$@"
    '';

    # ── Docker / Apptainer image ──────────────────────────────────────────────
    # Built from the same Nix derivations as the dev shell — bit-for-bit
    # identical Python environment.  Build with:
    #   nix build .#dockerImage && docker load < result
    # Push to GitHub Container Registry:
    #   skopeo copy nix:$(nix build .#dockerImage --print-out-paths --no-link) \
    #     docker://ghcr.io/ucsb-amo/potassium-workshop:latest
    # Pull with Apptainer (no root, no Docker required):
    #   apptainer pull docker://ghcr.io/ucsb-amo/potassium-workshop:latest
    dockerImage = pkgs.dockerTools.buildLayeredImage {
      name = "potassium-workshop";
      tag  = "latest";

      # Layers: Python env first (large, rarely changes), then tools.
      # buildLayeredImage splits these into separate layers so re-pulls after
      # small changes only download the diff.
      contents = [
        pythonEnv
        pkgs.bash
        pkgs.coreutils   # ls, mkdir, cat, etc.
        pkgs.git         # needed by manage_lab.sh inside the container
        pkgs.cacert      # TLS certs for git clone / pip
      ];

      config = {
        Entrypoint   = [ "${containerEntrypoint}" ];
        Cmd          = [ "${pkgs.bash}/bin/bash" ];
        WorkingDir   = "/workspace";
        # Declare /workspace as a volume so Docker/Apptainer knows to mount it.
        Volumes      = { "/workspace" = {}; };
        Labels = {
          "org.opencontainers.image.source"      = "https://github.com/ucsb-amo/POTASSIUM-WORKSHOP";
          "org.opencontainers.image.description" = "ARTIQ simulation environment for cold-K experiments";
        };
      };
    };

    # ── shellHook (identical to shell.nix) ────────────────────────────────────
    shellHook = ''
      WORKSPACE="$(pwd)"

      NIX_SITE="${pythonEnv}/${pkgs.python3.sitePackages}"
      export PYTHONPATH="$WORKSPACE/sim/stubs:$WORKSPACE:$WORKSPACE/artiq:$WORKSPACE/wax/waxx-src:$WORKSPACE/wax/waxa-src:$WORKSPACE/k-exp:$WORKSPACE/k-amo:$WORKSPACE/pyLabLib:$NIX_SITE"

      export data="$WORKSPACE/sim-data"
      export code="$WORKSPACE"

      mkdir -p "$WORKSPACE/sim-data"
      mkdir -p "$WORKSPACE/sim-data/logs"
      if [ ! -f "$WORKSPACE/sim-data/run_id.py" ]; then
        echo "1" > "$WORKSPACE/sim-data/run_id.py"
      fi
      if [ ! -f "$WORKSPACE/sim-data/device_state_config.json" ]; then
        echo '{"dds": {}, "dac": {}, "ttl": {}}' > "$WORKSPACE/sim-data/device_state_config.json"
      fi

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

  in {
    devShells.${system}.default = pkgs.mkShell {
      buildInputs = [ pythonEnv ];
      inherit shellHook;
    };

    packages.${system}.dockerImage = dockerImage;
  };
}
