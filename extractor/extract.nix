{ pkgs, extractor, ... }: user-js:
pkgs.runCommandLocal "user.nix" {} ''
  ${extractor}/bin/betterfox-extractor ${user-js}/user.js > $out
''