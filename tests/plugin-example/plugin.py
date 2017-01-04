import json

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from dce_plugin import PluginSDK


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")


class PluginJsonHandler(tornado.web.RequestHandler):
    def get(self):
        plugin_json = {
            "Name": "SDK-Test",
            "Extensions": {
                "daocloud.SDK-Test.navigatorNode": {
                    "ExtendedPoint": "dce.navigator.nodeSpecs",
                    "Object": {
                        "Title": "SDK-Test",
                        "ParentUID": "dce.core.navigator.plugins",
                        "Icon": "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+CiAgPHRpdGxlPnN1Y2Nlc3M8L3RpdGxlPgogIDxwYXRoIGQ9Ik0xNiwxLjJBMTQuOCwxNC44LDAsMSwwLDMwLjgsMTYsMTQuOCwxNC44LDAsMCwwLDE2LDEuMlpNMTMuNzczLDIzLjI2OEw2Ljk1NiwxNi40NTJsMi4xNzctMi4xNzcsNC42NCw0LjY0TDIyLjg2Nyw5LjgyLDI1LjA0NCwxMloiLz4KPC9zdmc+Cg==",
                        "NavigationTargetUID": "daocloud.SDK-Test.globalView"
                    }
                },
                "daocloud.SDK-Test.globalView": {
                    "ExtendedPoint": "dce.global.views",
                    "Object": {
                        "Name": "SDK-Test",
                        "ComponentClass": {
                            "ClassName": "dce.client.htmlbridge.HtmlView",
                            "Object": {
                                "Root": {
                                    "URL": "/config"
                                }
                            }
                        }
                    }
                }
            }
        }
        self.write(json.dumps(plugin_json))


class ConfigHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.sdk = PluginSDK()
        self.origin_config = {
            'key': 'Hello, World'
        }

    def post(self):
        saved = self.sdk.set_config(self.origin_config)
        self.write(json.dumps(saved))

    def get(self):
        retrived = self.sdk.get_config()
        self.write(json.dumps(retrived))


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/", MainHandler),
        (r"/config", ConfigHandler),
        (r"/plugin.json", PluginJsonHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(80)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
