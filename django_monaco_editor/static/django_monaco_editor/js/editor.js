require.config({paths: {'vs': '/static/external/monaco-editor/min/vs'}});

require(['vs/editor/editor.main'], function () {

  // 实际的textarea
  let contentELementList = document.querySelectorAll('textarea[use-monaco-editor="true"]')
  if (contentELementList.length === 0) {
    return
  }

  // 配置editor
  const editorElementList = document.querySelectorAll('#editor-id')
  const editorList = []
  for (let i = 0; i < editorElementList.length; i++) {
    let editorElement = editorElementList[i]
    let contentElement = contentELementList[i]
    editorList.push(monaco.editor.create(editorElement, {
        theme: 'vs-dark',
        cursorBlinking: 'smooth',
        fontSize: '14px',
        language: 'json',
        minimap: {
          enabled: true
        },
        value: JSON.stringify(JSON.parse(contentElement.value), null, 2),
      })
    )
  }

  // 监听提交表单操作，传值给实际的textarea
  let form = contentELementList[0].form;
  form.addEventListener('submit', function () {
      for (let i = 0; i < editorList.length; i++) {
        let editor = editorList[i]
        let contentElement = contentELementList[i]
        contentElement.value = editor.getValue();
      }
    }
  )
})