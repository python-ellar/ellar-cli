import os

from ellar.app import App, AppFactory
from ellar.common.constants import ELLAR_CONFIG_MODULE
from ellar.core import LazyModuleImport as lazyLoad

# from ellar.openapi import OpenAPIDocumentModule, OpenAPIDocumentBuilder, SwaggerUI


def bootstrap() -> App:
    application = AppFactory.create_from_app_module(
        lazyLoad("plain_project.root_module:ApplicationModule"),
        config_module=os.environ.get(
            ELLAR_CONFIG_MODULE, "plain_project.config:DevelopmentConfig"
        ),
        global_guards=[],
    )

    # uncomment this section if you want API documentation

    # document_builder = OpenAPIDocumentBuilder()
    # document_builder.set_title('Exy Title') \
    #     .set_version('1.0.2') \
    #     .set_contact(name='Author Name', url='https://www.author-name.com', email='authorname@gmail.com') \
    #     .set_license('MIT Licence', url='https://www.google.com')
    #
    # document = document_builder.build_document(application)
    # module = OpenAPIDocumentModule.setup(
    #    document=document,
    #    docs_ui=SwaggerUI(),
    #    guards=[]
    # )
    # application.install_module(module)
    return application
