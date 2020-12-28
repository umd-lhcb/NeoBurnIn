let
  pythonPackageOverlay = overlay: attr: self: super: {
    ${attr} = self.lib.fix (py:
      super.${attr}.override (old: {
        self = py;
        packageOverrides = self.lib.composeExtensions
          (old.packageOverrides or (_: _: { }))
          overlay;
      }));
  };
in
pythonPackageOverlay
  (self: super: {
    rainbow_logging_handler = super.callPackage ./rainbow_logging_handler { };
    aiojobs = super.callPackage ./aiojobs { };
    janus = super.callPackage ./janus { };
    curses-menu = super.callPackage ./curses-menu { };
  }) "python3"
