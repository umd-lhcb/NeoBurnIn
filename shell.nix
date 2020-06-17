let
  pkgs = import <nixpkgs> { overlays = [(import ./nix/burnin)]; };
  python = pkgs.python3;
  pythonPackages = python.pkgs;
in

pkgs.mkShell {
  name = "NeoBurnIn";
  buildInputs = with pythonPackages; [
    aiohttp
    aiohttp-cors
    janus
    pyyaml
    rainbow_logging_handler

    rpi_burnin
    labSNMP
  ];
}
