let
  pkgs = import <nixpkgs> { overlays = [(import ./nix/overlay)]; };
  python = pkgs.python3;
  pythonPackages = python.pkgs;
  stdenv = pkgs.stdenv;
in

pkgs.mkShell {
  name = "NeoBurnIn";
  buildInputs = with pythonPackages; [
    aiohttp
    aiohttp-cors
    aiojobs
    janus
    pyyaml
    rainbow_logging_handler

    rpi_burnin
    labSNMP
  ]
  ++ stdenv.lib.optionals (stdenv.isx86_64) [
    pytest
    matplotlib
  ];
}
