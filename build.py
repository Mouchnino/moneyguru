# Created By: Virgil Dupras
# Created On: 2009-12-30
# Copyright 2012 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import sys
import os
import os.path as op
import shutil
import json
import glob
import compileall
from argparse import ArgumentParser

from setuptools import setup, Extension

from hscommon import sphinxgen
from hscommon.plat import ISOSX
from hscommon.build import (print_and_do, copy_packages, move_all, copy, hardlink, filereplace,
    add_to_pythonpath, copy_sysconfig_files_for_embed, build_cocoalib_xibless, OSXAppStructure,
    build_cocoa_ext, copy_embeddable_python_dylib, collect_stdlib_dependencies)
from hscommon import loc
from hscommon.util import ensure_folder, modified_after, delete_files_with_pattern

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--clean', action='store_true', dest='clean',
        help="Clean build folder before building")
    parser.add_argument('--doc', action='store_true', dest='doc',
        help="Build only the help file")
    parser.add_argument('--loc', action='store_true', dest='loc',
        help="Build only localization")
    parser.add_argument('--updatepot', action='store_true', dest='updatepot',
        help="Generate .pot files from source code.")
    parser.add_argument('--mergepot', action='store_true', dest='mergepot',
        help="Update all .po files based on .pot files.")
    parser.add_argument('--cocoamod', action='store_true', dest='cocoamod',
        help="Build only Cocoa modules")
    parser.add_argument('--ext', action='store_true', dest='ext',
        help="Build only ext modules")
    parser.add_argument('--cocoa-compile', action='store_true', dest='cocoa_compile',
        help="Build only Cocoa executable")
    parser.add_argument('--xibless', action='store_true', dest='xibless',
        help="Build only xibless UIs")
    args = parser.parse_args()
    return args

def cocoa_compile_command():
    return '{0} waf configure && {0} waf'.format(sys.executable)

def cocoa_app():
    return OSXAppStructure('build/moneyGuru.app')

def build_xibless(dest='cocoa/autogen'):
    import xibless
    ensure_folder(dest)
    FNPAIRS = [
        ('lookup.py', 'MGLookup_UI'),
        ('schedule_scope_dialog.py', 'MGRecurrenceScopeDialog_UI'),
        ('custom_date_range_dialog.py', 'MGCustomDateRangePanel_UI'),
        ('account_reassign_panel.py', 'MGAccountReassignPanel_UI'),
        ('csv_layout_name.py', 'MGCSVLayoutNameDialog_UI'),
        ('csv_import_options.py', 'MGCSVImportOptions_UI'),
        ('import_window.py', 'MGImportWindow_UI'),
        ('export_panel.py', 'MGExportPanel_UI'),
        ('budget_panel.py', 'MGBudgetPanel_UI'),
        ('schedule_panel.py', 'MGSchedulePanel_UI'),
        ('mass_editing_panel.py', 'MGMassEditionPanel_UI'),
        ('transaction_panel.py', 'MGTransactionInspector_UI'),
        ('account_panel.py', 'MGAccountProperties_UI'),
        ('newtab_view.py', 'MGEmptyView_UI'),
        ('docprops_view.py', 'MGDocPropsView_UI'),
        ('cashculator_view.py', 'MGCashculatorView_UI'),
        ('transaction_view.py', 'MGTransactionView_UI'),
        ('account_view.py', 'MGAccountView_UI'),
        ('account_sheet_view.py', 'MGAccountSheetView_UI'),
        ('date_range_selector.py', 'MGDateRangeSelector_UI'),
        ('main_window.py', 'MGMainWindowController_UI'),
        ('preferences_panel.py', 'MGPreferencesPanel_UI'),
        ('main_menu.py', 'MGMainMenu_UI'),
    ]
    for srcname, dstname in FNPAIRS:
        srcpath = op.join('cocoa', 'ui', srcname)
        dstpath = op.join(dest, dstname)
        if modified_after(srcpath, dstpath + '.h'):
            xibless.generate(srcpath, dstpath, localizationTable='Localizable')

def build_cocoa(dev):
    print("Creating OS X app structure")
    app = cocoa_app()
    # We import this here because we don't want opened module to prevent us replacing .pyd files.
    from core.app import Application as MoneyGuruApp
    app_version = MoneyGuruApp.VERSION
    filereplace('cocoa/InfoTemplate.plist', 'build/Info.plist', version=app_version)
    app.create('build/Info.plist')
    print("Building localizations")
    build_localizations('cocoa')
    print("Building xibless UIs")
    build_cocoalib_xibless()
    build_xibless()
    print("Building Python extensions")
    build_cocoa_proxy_module()
    build_cocoa_bridging_interfaces()
    print("Building the cocoa layer")
    copy_embeddable_python_dylib('build')
    pydep_folder = op.join(app.resources, 'py')
    ensure_folder(pydep_folder)
    if dev:
        hardlink('cocoa/mg_cocoa.py', 'build/mg_cocoa.py')
    else:
        copy('cocoa/mg_cocoa.py', 'build/mg_cocoa.py')
    tocopy = ['core', 'hscommon', 'cocoalib/cocoa', 'objp', 'sgmllib']
    copy_packages(tocopy, pydep_folder, create_links=dev)
    sys.path.insert(0, 'build')
    collect_stdlib_dependencies('build/mg_cocoa.py', pydep_folder)
    del sys.path[0]
    copy_sysconfig_files_for_embed(pydep_folder)
    if not dev:
        # Important: Don't ever run delete_files_with_pattern('*.py') on dev builds because you'll
        # be deleting all py files in symlinked folders.
        compileall.compile_dir(pydep_folder, force=True, legacy=True)
        delete_files_with_pattern(pydep_folder, '*.py')
        delete_files_with_pattern(pydep_folder, '__pycache__')
    print("Compiling PSMTabBarControl framework")
    os.chdir('psmtabbarcontrol')
    print_and_do('{0} waf configure && {0} waf && {0} waf build_framework'.format(sys.executable))
    os.chdir('..')
    print("Compiling with WAF")
    os.chdir('cocoa')
    print_and_do(cocoa_compile_command())
    os.chdir('..')
    app.copy_executable('cocoa/build/moneyGuru')
    print("Copying resources and frameworks")
    resources = ['cocoa/dsa_pub.pem', 'build/mg_cocoa.py', 'build/help', 'plugin_examples'] + glob.glob('images/*')
    app.copy_resources(*resources, use_symlinks=dev)
    app.copy_frameworks('build/Python', 'cocoalib/Sparkle.framework',
        'psmtabbarcontrol/PSMTabBarControl.framework')
    print("Creating the run.py file")
    tmpl = open('run_template_cocoa.py', 'rt').read()
    run_contents = tmpl.replace('{{app_path}}', app.dest)
    open('run.py', 'wt').write(run_contents)

def build_qt(dev):
    qrc_path = op.join('qt', 'mg.qrc')
    pyrc_path = op.join('qt', 'mg_rc.py')
    print_and_do("pyrcc4 -py3 {0} > {1}".format(qrc_path, pyrc_path))
    print("Creating the run.py file")
    shutil.copy('run_template_qt.py', 'run.py')

def build_help(dev):
    if dev:
        print("Generating devdocs")
        print_and_do('sphinx-build devdoc devdoc_html')
    print("Generating Help")
    platform = 'osx' if ISOSX else 'win'
    current_path = op.abspath('.')
    confpath = op.join(current_path, 'help', 'conf.tmpl')
    help_basepath = op.join(current_path, 'help', 'en')
    help_destpath = op.join(current_path, 'build', 'help')
    changelog_path = op.join(current_path, 'help', 'changelog')
    tixurl = "https://hardcoded.lighthouseapp.com/projects/31473-moneyguru/tickets/{0}"
    confrepl = {'platform': platform}
    sphinxgen.gen(help_basepath, help_destpath, changelog_path, tixurl, confrepl, confpath)

def build_base_localizations():
    loc.compile_all_po('locale')
    loc.compile_all_po(op.join('hscommon', 'locale'))
    loc.merge_locale_dir(op.join('hscommon', 'locale'), 'locale')

def build_qt_localizations():
    loc.compile_all_po(op.join('qtlib', 'locale'))
    loc.merge_locale_dir(op.join('qtlib', 'locale'), 'locale')

def build_localizations(ui):
    build_base_localizations()
    if ui == 'cocoa':
        app = cocoa_app()
        loc.build_cocoa_localizations(app)
        locale_dest = op.join(app.resources, 'locale')
    elif ui == 'qt':
        build_qt_localizations()
        locale_dest = op.join('build', 'locale')
    if op.exists(locale_dest):
        shutil.rmtree(locale_dest)
    shutil.copytree('locale', locale_dest, ignore=shutil.ignore_patterns('*.po', '*.pot'))

def build_updatepot():
    if ISOSX:
        print("Updating Cocoa strings file.")
        build_cocoalib_xibless('cocoalib/autogen')
        loc.generate_cocoa_strings_from_code('cocoalib', 'cocoalib/en.lproj')
        # If we don't delete 'cocoalib/autogen', it messes with compilation
        shutil.rmtree('cocoalib/autogen')
        build_xibless()
        loc.generate_cocoa_strings_from_code('cocoa', 'cocoa/en.lproj')
    print("Building .pot files from source files")
    print("Building core.pot")
    loc.generate_pot(['core'], op.join('locale', 'core.pot'), ['tr'])
    print("Building columns.pot")
    loc.generate_pot(['core'], op.join('locale', 'columns.pot'), ['trcol'])
    print("Building ui.pot")
    loc.generate_pot(['qt'], op.join('locale', 'ui.pot'), ['tr'])
    print("Building hscommon.pot")
    loc.generate_pot(['hscommon'], op.join('hscommon', 'locale', 'hscommon.pot'), ['tr'])
    print("Building qtlib.pot")
    loc.generate_pot(['qtlib'], op.join('qtlib', 'locale', 'qtlib.pot'), ['tr'])
    if ISOSX:
        print("Building cocoalib.pot")
        cocoalib_pot = op.join('cocoalib', 'locale', 'cocoalib.pot')
        os.remove(cocoalib_pot)
        loc.strings2pot(op.join('cocoalib', 'en.lproj', 'cocoalib.strings'), cocoalib_pot)
        print("Enhancing ui.pot with Cocoa's strings files")
        loc.strings2pot(op.join('cocoa', 'en.lproj', 'Localizable.strings'), op.join('locale', 'ui.pot'))

def build_mergepot():
    print("Updating .po files using .pot files")
    loc.merge_pots_into_pos('locale')
    loc.merge_pots_into_pos(op.join('hscommon', 'locale'))
    loc.merge_pots_into_pos(op.join('qtlib', 'locale'))

def build_ext():
    print("Building C extensions")
    exts = []
    exts.append(Extension('_amount', [op.join('core', 'modules', 'amount.c')]))
    setup(
        script_args = ['build_ext', '--inplace'],
        ext_modules = exts,
    )
    move_all('_amount*', op.join('core', 'model'))

def build_cocoa_proxy_module():
    print("Building Cocoa Proxy")
    import objp.p2o
    objp.p2o.generate_python_proxy_code('cocoalib/cocoa/CocoaProxy.h', 'build/CocoaProxy.m')
    build_cocoa_ext("CocoaProxy", 'cocoalib/cocoa',
        ['cocoalib/cocoa/CocoaProxy.m', 'build/CocoaProxy.m', 'build/ObjP.m', 
            'cocoalib/HSErrorReportWindow.m', 'cocoa/autogen/HSErrorReportWindow_UI.m'],
        ['AppKit', 'CoreServices'],
        ['cocoalib', 'cocoa/autogen'])

def build_cocoa_bridging_interfaces():
    print("Building Cocoa Bridging Interfaces")
    import objp.o2p
    import objp.p2o
    import objp.const
    add_to_pythonpath('cocoa')
    add_to_pythonpath('cocoalib')
    from cocoa.inter import (PyGUIObject, GUIObjectView, PyTextField, PyTable, TableView, PyColumns,
        ColumnsView, PyOutline, PySelectableList, SelectableListView, PyFairware, FairwareView)
    # This createPool() business is a bit hacky, but upon importing mg_cocoa, we call
    # install_gettext_trans_under_cocoa() which uses proxy functions (and thus need an active
    # autorelease pool). If we don't do that, we get leak warnings.
    from cocoa import proxy
    proxy.createPool()
    from mg_cocoa import (PyPanel, PanelView, PyBaseView,
        PyTableWithDate, PyCompletableEdit, PyDateWidget,
        PyCSVImportOptions, CSVImportOptionsView, PyImportTable, PySplitTable, PyLookup, LookupView,
        PyDateRangeSelector, DateRangeSelectorView, PyImportWindow, ImportWindowView,
        PyFilterBar, FilterBarView, PyReport, ReportView, PyScheduleTable, PyBudgetTable,
        PyEntryTable, PyTransactionTable, PyGeneralLedgerTable, PyChart, ChartView,
        PyAccountPanel, PyMassEditionPanel, PyBudgetPanel, BudgetPanelView, PyCustomDateRangePanel,
        PyAccountReassignPanel, PyExportPanel, ExportPanelView, PyPanelWithTransaction,
        PanelWithTransactionView, PyTransactionPanel, PySchedulePanel, SchedulePanelView,
        BaseViewView, PyAccountSheetView, PyTransactionView,
        PyAccountView, AccountViewView, PyScheduleView, PyBudgetView, PyCashculatorView,
        PyGeneralLedgerView, PyDocPropsView, PyEmptyView, PyReadOnlyPluginView, PyMainWindow,
        MainWindowView, PyDocument, DocumentView, PyMoneyGuruApp)
    from mg_cocoa import PyPrintView, PySplitPrint, PyTransactionPrint, PyEntryPrint
    allclasses = [PyGUIObject, PyTextField, PyTable, PyColumns, PyOutline, PySelectableList,
        PyFairware, PyPanel, PyBaseView, PyTableWithDate, PyCompletableEdit, PyDateWidget,
        PyCSVImportOptions, PyImportTable, PySplitTable, PyLookup, PyDateRangeSelector,
        PyImportWindow, PyFilterBar, PyReport, PyScheduleTable, PyBudgetTable,
        PyEntryTable, PyTransactionTable, PyGeneralLedgerTable, PyChart, PyAccountPanel,
        PyMassEditionPanel, PyBudgetPanel, PyCustomDateRangePanel, PyAccountReassignPanel,
        PyExportPanel, PyPanelWithTransaction, PyTransactionPanel, PySchedulePanel,
        PyAccountSheetView, PyTransactionView, PyAccountView, PyScheduleView, PyBudgetView,
        PyCashculatorView, PyGeneralLedgerView, PyDocPropsView, PyEmptyView, PyReadOnlyPluginView,
        PyMainWindow, PyDocument, PyMoneyGuruApp]
    proxy.destroyPool()
    allclasses += [PyPrintView, PySplitPrint, PyTransactionPrint, PyEntryPrint]
    for class_ in allclasses:
        objp.o2p.generate_objc_code(class_, 'cocoa/autogen', inherit=True)
    allclasses = [GUIObjectView, TableView, ColumnsView, SelectableListView, FairwareView, 
        PanelView, CSVImportOptionsView, LookupView, DateRangeSelectorView, ImportWindowView,
        FilterBarView, ReportView, BudgetPanelView, ExportPanelView, PanelWithTransactionView,
        SchedulePanelView, BaseViewView, AccountViewView, MainWindowView,
        DocumentView, ChartView]
    clsspecs = [objp.o2p.spec_from_python_class(class_) for class_ in allclasses]
    objp.p2o.generate_python_proxy_code_from_clsspec(clsspecs, 'build/CocoaViews.m')
    py_folder = op.join(cocoa_app().resources, 'py')
    ensure_folder(py_folder)
    build_cocoa_ext('CocoaViews', py_folder, ['build/CocoaViews.m', 'build/ObjP.m'])
    import mg_const
    objp.const.generate_objc_code(mg_const, 'cocoa/autogen/PyConst.h')

def build_normal(ui, dev):
    build_help(dev)
    build_localizations(ui)
    build_ext()
    if ui == 'cocoa':
        build_cocoa(dev)
    elif ui == 'qt':
        build_qt(dev)

def main():
    args = parse_args()
    conf = json.load(open('conf.json'))
    ui = conf['ui']
    dev = conf['dev']
    print("Building moneyGuru with UI {}".format(ui))
    if dev:
        print("Building in Dev mode")
    if args.clean:
        if op.exists('build'):
            shutil.rmtree('build')
    if not op.exists('build'):
        os.mkdir('build')
    if args.doc:
        build_help(dev)
    elif args.loc:
        build_localizations(ui)
    elif args.updatepot:
        build_updatepot()
    elif args.mergepot:
        build_mergepot()
    elif args.cocoamod:
        build_cocoa_proxy_module()
        build_cocoa_bridging_interfaces()
    elif args.ext:
        build_ext()
    elif args.cocoa_compile:
        os.chdir('cocoa')
        print_and_do(cocoa_compile_command())
        os.chdir('..')
        cocoa_app().copy_executable('cocoa/build/moneyGuru')
    elif args.xibless:
        build_cocoalib_xibless()
        build_xibless()
    else:
        build_normal(ui, dev)

if __name__ == '__main__':
    main()
