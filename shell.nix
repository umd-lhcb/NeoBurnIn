let
  pkgs = import <nixpkgs> {};
  python = pkgs.python3;
  pythonPackages = python.pkgs;
in

pkgs.mkShell {
  name = "pip-env";
  buildInputs = with pythonPackages; [
    # Python requirements (enough to get a virtualenv going).
    virtualenvwrapper
    hidapi
    aiohttp
    aiohttp-cors
    janus
    PyYAML
    RPI_GPIO
    rainbow_logging_handler
  ];

  shellHook = ''
    # Allow the use of wheels.
    SOURCE_DATE_EPOCH=$(date +%s)

    VENV=./.virtualenv
    if test ! -d $VENV; then
      virtualenv $VENV
    fi
    source $VENV/bin/activate

    # allow for the environment to pick up packages installed with virtualenv
    export PYTHONPATH=$VENV/${python.sitePackages}/:$PYTHONPATH
  '';
}
