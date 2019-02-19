import inspect
import os
import pkgutil


class Plugin:
    """
    该基类每个插件都需要继承，插件需要实现基类定义的方法"""
    def __init__(self):
        self.description = '未知'

    def perform_operation(self, argument):
        """
        实际执行插件所执行的方法，该方法所有插件类都需要实现
        """
        raise NotImplementedError


class PluginCollection:
    """
    该类会通过传入的package查找继承了Plugin类的插件类
    """
    def __init__(self, plugin_package):
        self.plugin_package = plugin_package
        self.reload_plugins()

    def reload_plugins(self):
        """
        重置plugins列表，遍历传入的package查询有效的插件
        """
        self.plugins = []
        self.seen_paths = []
        print()
        print(f"在 {self.plugin_package} 包里查找插件")
        self.walk_package(self.plugin_package)

    def apply_all_plugins_on_value(self, argument):
        print()
        print(f"执行参数 {argument} 到所有的插件:")
        for plugin in self.plugins:
            print(f"    执行 {plugin.description} 参数 {argument} 结果 {plugin.perform_operation(argument)}")


    def walk_package(self, package):
        """
        递归遍历包里获取所有的插件
        """
        imported_package = __import__(package, fromlist=['blah'])
        
        for _, pluginname, ispkg in pkgutil.iter_modules(imported_package.__path__, imported_package.__name__ + '.'):
            if not ispkg:
                plugin_module = __import__(pluginname, fromlist=['blah'])
                clsmembers = inspect.getmembers(plugin_module, inspect.isclass)
                for (_, c) in clsmembers:
                    # 仅加入Plugin类的子类，忽略掉Plugin本身
                    if issubclass(c, Plugin) and (c is not Plugin):
                        print(f'    找到插件类: {c.__module__}.{c.__name__}')
                        self.plugins.append(c())

        # 现在我们已经查找了当前package中的所有模块，现在我们递归查找子packages里的附件模块
        all_current_paths = []
        if isinstance(imported_package.__path__, str):
            all_current_paths.append(imported_package.__path__)
        else:
            all_current_paths.extend([x for x in imported_package.__path__])
        
        for pkg_path in all_current_paths:
            if pkg_path not in self.seen_paths:
                self.seen_paths.append(pkg_path)

                # 获取当前package中的子目录
                child_pkgs = [p for p in os.listdir(pkg_path) if os.path.isdir(os.path.join(pkg_path, p))]

                # 递归遍历子目录的package
                for child_pkg in child_pkgs:
                    self.walk_package(package + '.' + child_pkg)
