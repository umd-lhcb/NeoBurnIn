{
  description = "Server and client implemented for the UT boards burn in process.";

  inputs = rec {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-20.09";
    flake-utils.url = "github:numtide/flake-utils";
    labSNMP = {
      url = "github:umd-lhcb/labSNMP";
      inputs = {
        inherit nixpkgs flake-utils;
      };
    };
    rpi_burnin = {
      url = "github:umd-lhcb/rpi.burnin";
      inputs = {
        inherit nixpkgs flake-utils;
      };
    };
  };

  outputs = { self, nixpkgs, flake-utils, labSNMP, rpi_burnin }:
    {
      overlay = import ./nix/overlay.nix;
    }
    //
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
        python = pkgs.python3;
        pythonPackages = python.pkgs;
        stdenv = pkgs.stdenv;
      in
      rec {
        packages = rec {
          NeoBurnIn = python.withPackages (ps: with ps; [
            aiohttp
            aiohttp-cors
            aiojobs
            janus
            pyyaml
            rainbow_logging_handler
          ]);
          NeoBurnIn_Dev = pkgs.mkShell {
            buildInputs = [ NeoBurnIn ]
            ++ stdenv.lib.optionals (stdenv.isx86_64) (with pythonPackages; [
              # Testing
              pytest

              # Python auto-complete
              jedi

              # Linters
              flake8
              pylint

              # Plotting
              matplotlib
            ]);
          };
        };
        devShell = packages.NeoBurnIn_Dev;
      });
}
