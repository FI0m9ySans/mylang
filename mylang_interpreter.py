import re
import sys
import os
import traceback

class MyLangError(Exception):
    """自定义语言错误基类"""
    pass

class LexerError(MyLangError):
    """词法分析错误"""
    pass

class ParserError(MyLangError):
    """语法分析错误"""
    pass

class RuntimeError(MyLangError):
    """运行时错误"""
    pass

# 标记类型
class TokenType:
    PRINT = "打印"
    STRING = "字符串"
    NUMBER = "数字"
    IDENTIFIER = "标识符"
    SEMICOLON = "分号"
    LPAREN = "左括号"
    RPAREN = "右括号"
    LBRACE = "左大括号"
    RBRACE = "右大括号"
    EOF = "文件结束"
    ASSIGN = "赋值"
    IF = "如果"
    ELSE = "否则"
    WHILE = "循环"
    COMPARISON = "比较"
    PLUS = "加号"
    MINUS = "减号"
    MULTIPLY = "乘号"
    DIVIDE = "除号"
    IMPORT = "导入"
    TRY = "尝试"
    CATCH = "捕获"

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', 行:{self.line}, 列:{self.column})"

# 词法分析器
class Lexer:
    def __init__(self, text, filename="<unknown>"):
        self.text = text
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.text else None
    
    def error(self, msg):
        raise LexerError(f"{self.filename}:{self.line}:{self.column}: {msg}")
    
    def advance(self):
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        # 跳过单行注释
        while self.current_char is not None and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()
    
    def string(self):
        result = ""
        start_line = self.line
        start_column = self.column
        self.advance()  # 跳过开头的引号
        
        while self.current_char is not None and self.current_char != '"':
            # 处理转义字符
            if self.current_char == '\\':
                self.advance()
                if self.current_char == 'n':
                    result += '\n'
                elif self.current_char == 't':
                    result += '\t'
                elif self.current_char == '"':
                    result += '"'
                elif self.current_char == '\\':
                    result += '\\'
                else:
                    self.error(f"未知的转义序列: \\{self.current_char}")
                self.advance()
            else:
                result += self.current_char
                self.advance()
                
        if self.current_char == '"':
            self.advance()
        else:
            self.error("未结束的字符串")
        return result
    
    def number(self):
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()
            return float(result)
        return int(result)
    
    def identifier(self):
        result = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # 检查是否为关键字
        keywords = {
            '打印': TokenType.PRINT,
            '如果': TokenType.IF,
            '否则': TokenType.ELSE,
            '循环': TokenType.WHILE,
            '导入': TokenType.IMPORT,
            '尝试': TokenType.TRY,
            '捕获': TokenType.CATCH
        }
        return keywords.get(result, TokenType.IDENTIFIER), result
    
    def get_next_token(self):
        while self.current_char is not None:
            # 跳过空白字符
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # 跳过注释
            if self.current_char == '#':
                self.skip_comment()
                continue
            
            # 字符串
            if self.current_char == '"':
                return Token(TokenType.STRING, self.string(), self.line, self.column)
            
            # 数字
            if self.current_char.isdigit():
                return Token(TokenType.NUMBER, self.number(), self.line, self.column)
            
            # 标识符和关键字
            if self.current_char.isalpha() or self.current_char == '_':
                token_type, value = self.identifier()
                return Token(token_type, value, self.line, self.column)
            
            # 单字符标记
            if self.current_char == ';':
                token = Token(TokenType.SEMICOLON, ';', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '(':
                token = Token(TokenType.LPAREN, '(', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == ')':
                token = Token(TokenType.RPAREN, ')', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '{':
                token = Token(TokenType.LBRACE, '{', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '}':
                token = Token(TokenType.RBRACE, '}', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '+':
                token = Token(TokenType.PLUS, '+', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '-':
                token = Token(TokenType.MINUS, '-', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '*':
                token = Token(TokenType.MULTIPLY, '*', self.line, self.column)
                self.advance()
                return token
            
            if self.current_char == '/':
                token = Token(TokenType.DIVIDE, '/', self.line, self.column)
                self.advance()
                return token
            
            # 多字符标记
            if self.current_char == '=':
                start_line = self.line
                start_column = self.column
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(TokenType.COMPARISON, '==', start_line, start_column)
                return Token(TokenType.ASSIGN, '=', start_line, start_column)
            
            if self.current_char in ['<', '>', '!']:
                start_line = self.line
                start_column = self.column
                op = self.current_char
                self.advance()
                if self.current_char == '=':
                    op += self.current_char
                    self.advance()
                return Token(TokenType.COMPARISON, op, start_line, start_column)
            
            self.error(f"无法识别的字符: '{self.current_char}'")
        
        return Token(TokenType.EOF, None, self.line, self.column)

# AST节点类
class AST:
    pass

class Print(AST):
    def __init__(self, expr):
        self.expr = expr

class Assign(AST):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

class Variable(AST):
    def __init__(self, name):
        self.name = name

class Number(AST):
    def __init__(self, value):
        self.value = value

class String(AST):
    def __init__(self, value):
        self.value = value

class If(AST):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

class While(AST):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

class Comparison(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class Import(AST):
    def __init__(self, module_name):
        self.module_name = module_name

# 添加 TryCatch AST 节点
class TryCatch(AST):
    def __init__(self, try_block, catch_block, error_var="_error"):
        self.try_block = try_block
        self.catch_block = catch_block
        self.error_var = error_var

# 语法分析器
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
    
    def error(self, msg, token=None):
        if token is None:
            token = self.current_token
        raise ParserError(f"{self.lexer.filename}:{token.line}:{token.column}: {msg}")
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"期望 {token_type}, 得到 {self.current_token.type}")
    
    def factor(self):
        token = self.current_token
        
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Number(token.value)
        
        if token.type == TokenType.STRING:
            self.eat(TokenType.STRING)
            return String(token.value)
        
        if token.type == TokenType.IDENTIFIER:
            self.eat(TokenType.IDENTIFIER)
            return Variable(token.value)
        
        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        
        self.error(f"意外的标记: {token.type}")
    
    def term(self):
        node = self.factor()
        
        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            if token.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif token.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)
            
            node = BinOp(left=node, op=token.value, right=self.factor())
        
        return node
    
    def expr(self):
        node = self.term()
        
        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)
            
            node = BinOp(left=node, op=token.value, right=self.term())
        
        return node
    
    def comparison(self):
        node = self.expr()
        
        if self.current_token.type == TokenType.COMPARISON:
            token = self.current_token
            self.eat(TokenType.COMPARISON)
            node = Comparison(left=node, op=token.value, right=self.expr())
        
        return node
    
    def statement(self):
        token = self.current_token
        
        if token.type == TokenType.PRINT:
            self.eat(TokenType.PRINT)
            self.eat(TokenType.LPAREN)
            expr = self.expr()
            self.eat(TokenType.RPAREN)
            self.eat(TokenType.SEMICOLON)
            return Print(expr)
        
        if token.type == TokenType.IDENTIFIER:
            var_name = token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.ASSIGN)
            expr = self.expr()
            self.eat(TokenType.SEMICOLON)
            return Assign(var_name, expr)
        
        if token.type == TokenType.IF:
            self.eat(TokenType.IF)
            self.eat(TokenType.LPAREN)
            condition = self.comparison()
            self.eat(TokenType.RPAREN)
            self.eat(TokenType.LBRACE)
            true_block = self.block()
            self.eat(TokenType.RBRACE)
            
            false_block = None
            if self.current_token.type == TokenType.ELSE:
                self.eat(TokenType.ELSE)
                self.eat(TokenType.LBRACE)
                false_block = self.block()
                self.eat(TokenType.RBRACE)
            
            return If(condition, true_block, false_block)
        
        if token.type == TokenType.WHILE:
            self.eat(TokenType.WHILE)
            self.eat(TokenType.LPAREN)
            condition = self.comparison()
            self.eat(TokenType.RPAREN)
            self.eat(TokenType.LBRACE)
            block = self.block()
            self.eat(TokenType.RBRACE)
            return While(condition, block)
        
        if token.type == TokenType.IMPORT:
            self.eat(TokenType.IMPORT)
            if self.current_token.type != TokenType.STRING:
                self.error("期望字符串作为模块名")
            module_name = self.current_token.value
            self.eat(TokenType.STRING)
            self.eat(TokenType.SEMICOLON)
            return Import(module_name)
        
        if token.type == TokenType.TRY:
            self.eat(TokenType.TRY)
            self.eat(TokenType.LBRACE)
            try_block = self.block()
            self.eat(TokenType.RBRACE)

            self.eat(TokenType.CATCH)
            error_var = "_error"  # 默认错误变量名
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                if self.current_token.type == TokenType.IDENTIFIER:
                    error_var = self.current_token.value
                    self.eat(TokenType.IDENTIFIER)
                self.eat(TokenType.RPAREN)

            self.eat(TokenType.LBRACE)
            catch_block = self.block()
            self.eat(TokenType.RBRACE)

            return TryCatch(try_block, catch_block, error_var)

        self.error(f"意外的语句: {token.type}")
    
    def block(self):
        statements = []
        while self.current_token.type not in (TokenType.RBRACE, TokenType.EOF):
            statements.append(self.statement())
        return statements
    
    def parse(self):
        statements = []
        while self.current_token.type != TokenType.EOF:
            statements.append(self.statement())
        return statements

# 解释器
class Interpreter:
    def __init__(self):
        self.variables = {}
        self.imported_modules = set()
    
    def visit(self, node):
        try:
            method_name = f'visit_{type(node).__name__}'
            method = getattr(self, method_name, self.generic_visit)
            return method(node)
        except RuntimeError as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"运行时错误: {str(e)}")
    
    def generic_visit(self, node):
        raise RuntimeError(f"没有 visit_{type(node).__name__} 方法")
    
    def visit_Number(self, node):
        return node.value
    
    def visit_String(self, node):
        return node.value
    
    def visit_Variable(self, node):
        if node.name in self.variables:
            return self.variables[node.name]
        else:
            available_vars = ", ".join(self.variables.keys())
            raise RuntimeError(f"未定义的变量: '{node.name}'。可用的变量: [{available_vars}]")
    
    def visit_Assign(self, node):
        value = self.visit(node.expr)
        self.variables[node.var] = value
        return value
    
    def visit_Print(self, node):
        value = self.visit(node.expr)
        print(value)
        return value
    
    def visit_Comparison(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # 类型检查
        if type(left) != type(right):
            raise RuntimeError(f"比较运算类型不匹配: {type(left).__name__} 和 {type(right).__name__}")
        
        if node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        elif node.op == '<':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left < right
            else:
                raise RuntimeError(f"不支持的类型比较: {type(left).__name__} < {type(right).__name__}")
        elif node.op == '<=':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left <= right
            else:
                raise RuntimeError(f"不支持的类型比较: {type(left).__name__} <= {type(right).__name__}")
        elif node.op == '>':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left > right
            else:
                raise RuntimeError(f"不支持的类型比较: {type(left).__name__} > {type(right).__name__}")
        elif node.op == '>=':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left >= right
            else:
                raise RuntimeError(f"不支持的类型比较: {type(left).__name__} >= {type(right).__name__}")
        else:
            raise RuntimeError(f"未知的比较运算符: {node.op}")
    
    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # 类型检查和运算
        if node.op == '+':
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left + right
            else:
                raise RuntimeError(f"不支持的类型相加: {type(left).__name__} + {type(right).__name__}")
        elif node.op == '-':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left - right
            else:
                raise RuntimeError(f"不支持的类型相减: {type(left).__name__} - {type(right).__name__}")
        elif node.op == '*':
            if isinstance(left, str) and isinstance(right, int):
                return left * right
            elif isinstance(left, int) and isinstance(right, str):
                return right * left
            elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
                return left * right
            else:
                raise RuntimeError(f"不支持的类型相乘: {type(left).__name__} * {type(right).__name__}")
        elif node.op == '/':
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if right == 0:
                    raise RuntimeError("除以零错误")
                return left / right
            else:
                raise RuntimeError(f"不支持的类型相除: {type(left).__name__} / {type(right).__name__}")
        else:
            raise RuntimeError(f"未知的运算符: {node.op}")
    
    def visit_If(self, node):
        condition = self.visit(node.condition)
        if not isinstance(condition, bool):
            raise RuntimeError(f"条件表达式必须为布尔值，得到: {type(condition).__name__}")
            
        if condition:
            for stmt in node.true_block:
                self.visit(stmt)
        elif node.false_block:
            for stmt in node.false_block:
                self.visit(stmt)
    
    def visit_While(self, node):
        max_iterations = 10000  # 防止无限循环
        iterations = 0
        
        while self.visit(node.condition):
            for stmt in node.block:
                self.visit(stmt)
            
            iterations += 1
            if iterations > max_iterations:
                raise RuntimeError("循环次数过多，可能陷入无限循环")
    
    def visit_Import(self, node):
        module_name = node.module_name
        if module_name in self.imported_modules:
            return  # 避免重复导入
        
        self.imported_modules.add(module_name)
        
        # 查找模块文件
        module_path = self.find_module(module_name)
        if not module_path:
            raise RuntimeError(f"找不到模块: {module_name}")
        
        # 读取并执行模块代码
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                module_code = f.read()
        except Exception as e:
            raise RuntimeError(f"无法读取模块文件 '{module_path}': {str(e)}")
        
        # 创建新的解释器实例来执行模块代码
        module_interpreter = Interpreter()
        module_interpreter.variables = self.variables  # 共享变量空间
        
        try:
            lexer = Lexer(module_code, module_path)
            parser = Parser(lexer)
            ast = parser.parse()
            module_interpreter.interpret(ast)
        except MyLangError as e:
            raise RuntimeError(f"导入模块 '{module_name}' 时出错: {str(e)}")
    
    def find_module(self, module_name):
        # 在当前目录查找
        if os.path.exists(f"{module_name}.mylang"):
            return f"{module_name}.mylang"
        
        # 在包目录查找
        package_dir = os.path.join(os.path.expanduser("~"), ".mylang", "packages")
        if os.path.exists(os.path.join(package_dir, f"{module_name}.mylang")):
            return os.path.join(package_dir, f"{module_name}.mylang")
        
        # 查找带版本号的包
        if os.path.exists(package_dir):
            for filename in os.listdir(package_dir):
                if filename.startswith(f"{module_name}-") and filename.endswith(".mylang"):
                    return os.path.join(package_dir, filename)
        
        return None
    
    def visit_TryCatch(self, node):
        try:
            for stmt in node.try_block:
                self.visit(stmt)
        except Exception as e:
            # 保存错误信息到变量
            self.variables[node.error_var] = str(e)
            for stmt in node.catch_block:
                self.visit(stmt)

    def interpret(self, ast):
        for node in ast:
            self.visit(node)

# 主函数
def main():
    if len(sys.argv) > 1:
        # 从文件读取
        filename = sys.argv[1]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"错误: 无法读取文件 '{filename}': {str(e)}")
            return 1
    else:
        # 交互式模式
        print("MyLang 交互式解释器 (输入 '退出' 结束)")
        lines = []
        while True:
            try:
                line = input("> ")
                if line.strip() == '退出':
                    break
                lines.append(line)
            except (EOFError, KeyboardInterrupt):
                print("\n再见!")
                break
        text = '\n'.join(lines)
    
    try:
        lexer = Lexer(text, filename if len(sys.argv) > 1 else "<stdin>")
        parser = Parser(lexer)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        return 0
    except MyLangError as e:
        print(f"错误: {e}")
        return 1
    except Exception as e:
        print(f"意外错误: {e}")
        if len(sys.argv) > 1:  # 只在文件模式下显示详细错误
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())