from flask import Flask, request, jsonify
import jupyter_client

app = Flask(__name__)

class Interpreter:
    def __init__(self):
        self.kernel_manager = jupyter_client.KernelManager()
        self.kernel_manager.start_kernel()
        self.kernel = self.kernel_manager.blocking_client()

    def execute(self, code: str) -> str:
        self.kernel.execute(code)
        shell_msg = self.kernel.get_shell_msg()
        msg_out = self.kernel.get_iopub_msg()['content']
        return shell_msg, msg_out

interpreter = Interpreter()

@app.route('/api/v1/exec', methods=['POST'])
def exec_code():
    data = request.json
    code = data.get('code', '')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    try:
        shell_msg, msg_out = interpreter.execute(code)
        return jsonify({"shell_msg": shell_msg, "msg_out": msg_out})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8888)
