from snippets import Icon, generate

generate(
    "source.cmake",
    snippets={
        "pl": "message($SEL0)",
    },
    completions={
        ("Function", Icon.FUNCTION): [
            "add_executable",
            "add_library",
            "add_subdirectory",
            "target_compile_options",
            "target_compile_definitions",
            "target_include_directories",
            "target_link_directories",
            "target_link_libraries",
            "target_sources",
        ],
        ("Block", Icon.BLOCK): [
            "function($1)<=>endfunction()",
            "if($1)<=>endif()",
            "macro($1)<=>endmacro()",
        ],
        ("Variable", Icon.VARIABLE): [
            "CMAKE_BINARY_DIR",
            "CMAKE_CURRENT_BINARY_DIR",
            "CMAKE_CURRENT_SOURCE_DIR",
            "CMAKE_SOURCE_DIR",
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
        ]
    },
)
