from flask import Flask, request, jsonify
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

app = Flask(__name__)

notebook = nbformat.v4.new_notebook()

@app.route('/api/v1/exec', methods=['POST'])
def execute_code():
    data = request.json
    code = data['code']
    # 创建一个新的 Notebook
    
    notebook.cells.append(nbformat.v4.new_code_cell(code))

    # 执行 Notebook
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')

    # 执行并输出结果
    return jsonify({'result': ep.preprocess(notebook, {'metadata': {'path': './'}})})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8888)
