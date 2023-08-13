from snippets import Icon, generate

generate(
    "source.cmake",
    snippets={
        "pl": "message($SEL0)",
    },
    completions={
        ("Function", Icon.FUNCTION): [
            "add_dependencies",
            "add_executable",
            "add_library",
            "add_subdirectory",
            "install",
            "set_target_properties",
            "target_compile_definitions",
            "target_compile_options",
            "target_include_directories",
            "target_link_directories",
            "target_link_libraries",
            "target_sources",
        ],
        ("Block", Icon.BLOCK): [
            "function($1)<=>endfunction()",
            "if($1)<=>endif()",
            "foreach($1)<=>endforeach()",
            "macro($1)<=>endmacro()",
        ],
        ("Variable", Icon.CONSTANT): [
            "CMAKE_BINARY_DIR",
            "CMAKE_CURRENT_BINARY_DIR",
            "CMAKE_CURRENT_SOURCE_DIR",
            "CMAKE_INSTALL_PREFIX",
            "CMAKE_SOURCE_DIR",
            "CMAKE_SYSTEM_NAME",
        ],
    },
)

generate(
    "source.cmake meta.function-call",
    completions={
        ("Constant", Icon.ACCESS_MODIFIER): [
            "PUBLIC",
            "PRIVATE",
            "INTERFACE",
        ],
        ("Operator", Icon.KEYWORD): [
            "IN_LIST",
            "STREQUAL",
        ],
    },
)
