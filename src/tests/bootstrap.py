# -*- encoding: utf-8 -*-
import os

from mailbundle.buildconf import bootstrap


def test_bootstrap(tmpdir):
    bundle_dir = tmpdir / "test_bundle"

    bootstrap(bundle_dir.dirpath(), None, None)

    baselvl = os.listdir(bundle_dir.dirpath())

    assert "var" in baselvl
    assert "settings" in baselvl
    assert "environment" in baselvl

    varlvl = os.listdir(bundle_dir.dirpath().join("var"))

    assert "mail" in varlvl
    assert "lib" in varlvl

    settingslvl = os.listdir(bundle_dir.dirpath().join("settings"))

    assert "vars" in settingslvl
    assert "overrides" in settingslvl
