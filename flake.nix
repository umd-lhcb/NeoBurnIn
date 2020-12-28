{
  description = "Server and client implemented for the UT boards burn in process.";

  inputs = rec {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-20.09";
    flake-utils.url = "github:numtide/flake-utils";
    labSNMP = {
      url = "github:umd-lhcb/labSNMP";
      inputs = {
        inherit nixpkgs flake-utils};
      };
      rpi_burnin = {
        url = "github:umd-lhcb/rpi.burnin";
        inputs = {
          inherit nixpkgs flake-utils};
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
              overlays = [ self.overlay labSNMP.overlay rpi_burnin.overlay ];
            };
            python = pkgs.python3;
            pythonPackages = python.pkgs;
            stdenv = pkgs.stdenv;
          in
          {
            devShell = pkgs.mkShell {
              name = "NeoBurnIn";
              buildInputs = with pythonPackages; [
                pkgs.pythonPackages.NeoBurnIn
              ]
              ++ stdenv.lib.optionals (stdenv.isx86_64) [
                # Python auto-complete
                jedi

                # Linters
                flake8
                pylint

                # Plotting
                matplotlib
              ];
            };
          });
    }
