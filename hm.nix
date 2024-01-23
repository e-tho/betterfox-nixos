versions: extracted: {
  config,
  lib,
  ...
}: let
  inherit (lib) types;

  cfg = config.programs.firefox;
  version = "${config.programs.firefox.package.version}";
  ext = extracted."${cfg.betterfox.version}";
in {
  options.programs.firefox = {
    betterfox = {
      enable = lib.mkEnableOption "betterfox support in profiles";
      version = lib.mkOption {
        description = "The version of betterfox user.js used";
        type = types.enum versions;
        default = "master";
      };
    };
    profiles = lib.mkOption {
      type = types.attrsOf (types.submodule ({config, ...}: {
        options.betterfox = lib.mkOption {
          description = "Setup betterfox user.js in profile";
          type = import ./type.nix {
            extracted = ext;
            inherit lib;
          };
          default = {};
        };
        config = lib.mkIf cfg.betterfox.enable {
          settings = config.betterfox.flatSettings;
        };
      }));
    };
  };

  config = lib.mkIf (cfg.enable && cfg.betterfox.enable && !(lib.hasPrefix cfg.betterfox.version version)) {
    warnings = [
      "Betterfox version ${cfg.betterfox.version} does not match Firefox's (${version})"
    ];
  };
}
