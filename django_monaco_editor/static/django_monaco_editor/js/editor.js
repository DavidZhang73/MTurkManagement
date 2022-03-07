require.config({paths: {'vs': '/static/external/monaco-editor/min/vs'}});

require(['vs/editor/editor.main'], function () {

    // 实际的textarea
    let content = document.querySelector('textarea[use-monaco-editor="true"]')
    if (!content) {
        return
    }

    // 配置editor
    let editor = monaco.editor.create(document.getElementById('editor-id'), {
        theme: 'vs-dark',
        cursorBlinking: 'smooth',
        fontSize: '14px',
        language: 'json',
        minimap: {
            enabled: true
        },
        value: JSON.stringify(JSON.parse(content.value), null, 2),
    });

        // 监听提交表单操作，传值给实际的textarea
        let form = content.form;
        form.addEventListener('submit', function () {
            content.value = editor.getValue();
        });
    }
});

