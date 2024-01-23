{
  description = "Utilities to use betterfox's user.js for Firefox";

  inputs = {
    nixpkgs.url = "nixpkgs/release-23.05";
    flake-compat = {
      url = "github:edolstra/flake-compat";
      flake = false;
    };
    pre-commit.url = "github:cachix/pre-commit-hooks.nix";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    pre-commit,
    flake-utils,
    ...
  }: let
    inherit (nixpkgs.lib) mapAttrs' nameValuePair;

    ppVer = builtins.replaceStrings ["."] ["_"];
    docs = pkgs:
      (mapAttrs'
        (version: extracted:
          nameValuePair "betterfox-v${ppVer version}-doc-static"
          (pkgs.callPackage ./doc {inherit extracted version;}))
        self.lib.betterfox.extracted)
      // (mapAttrs'
        (version: extracted:
          nameValuePair "betterfox-v${ppVer version}-doc"
          (pkgs.callPackage ./doc {
            inherit extracted version;
            css = "/style.css";
          }))
        self.lib.betterfox.extracted);

    outputs = flake-utils.lib.eachDefaultSystem (system: let
      pkgs = nixpkgs.legacyPackages."${system}";
      extractor = pkgs.callPackage ./extractor {};
      generator = pkgs.callPackage ./generator {betterfox-extractor = extractor;};
    in {
      checks.pre-commit-check = pre-commit.lib."${system}".run {
        src = ./.;
        hooks = {
          alejandra.enable = true;
          deadnix.enable = true;
          statix.enable = true;
          perltidy = {
            enable = true;
            name = "Tidy perl code";
            types = ["perl"];
            entry = "${pkgs.perl.passthru.pkgs.PerlTidy}/bin/perltidy -b";
          };
        };
        settings = {
          alejandra.exclude = ["autogen"];
          statix.ignore = ["autogen/*"];
        };
      };

      packages =
        {
          betterfox-extractor = extractor;
          betterfox-generator = generator;
          betterfox-doc-css = pkgs.writeText "style.css" (builtins.readFile ./doc/style.css);
          default = extractor;
        }
        // (docs pkgs);
    });
  in
    outputs
    // {
      overlays = {
        betterfox = _: prev: (let
          extractor = prev.callPackage ./extractor {};
        in
          {
            betterfox-extractor = prev.callPackage ./extractor {};
            betterfox-generator = prev.callPackage ./generator {betterfox-extractor = extractor;};
            betterfox-doc-css = prev.writeText "style.css" (builtins.readFile ./doc/style.css);
          }
          // (docs prev));
        default = self.overlays.betterfox;
      };

      lib.betterfox = {
        supportedVersions = builtins.attrNames self.lib.betterfox.extracted;
        extracted = import ./autogen;
      };

      hmModules = {
        betterfox = import ./hm.nix self.lib.betterfox.supportedVersions self.lib.betterfox.extracted;
        default = self.hmModules.betterfox;
      };
    };
}
