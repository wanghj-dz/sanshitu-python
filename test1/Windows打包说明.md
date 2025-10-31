# Windows系统打包说明

本文档说明如何在Windows系统上将Python程序打包成exe可执行文件。

## 方法一:使用提供的打包脚本(推荐)

### 步骤

1. **安装Python环境**
   - 下载Python 3.11或更高版本:[https://www.python.org/downloads/](https://www.python.org/downloads/)
   - 安装时勾选"Add Python to PATH"选项

2. **运行打包脚本**
   - 双击运行`打包程序.bat`文件
   - 等待打包完成(约2-3分钟)
   - 打包完成后,exe文件位于`dist`文件夹中

3. **运行程序**
   - 进入`dist`文件夹
   - 双击`投影实验程序.exe`即可运行

## 方法二:手动打包

### 步骤

1. **安装依赖**
   ```cmd
   pip install numpy matplotlib pyinstaller
   ```

2. **打包命令**
   ```cmd
   pyinstaller --onefile --windowed --name "投影实验程序" projection_experiment.py
   ```

3. **查找exe文件**
   - 打包完成后,exe文件位于`dist`文件夹中

## 常见问题

### Q1: 提示"pip不是内部或外部命令"
**解决方法**: Python安装时未勾选"Add Python to PATH",需要重新安装Python并勾选该选项。

### Q2: 打包过程中出现错误
**解决方法**: 
- 确保Python版本为3.11或更高
- 尝试使用管理员权限运行命令提示符
- 检查网络连接是否正常

### Q3: exe文件无法运行
**解决方法**:
- 检查Windows防火墙或杀毒软件是否拦截
- 右键点击exe文件,选择"以管理员身份运行"

### Q4: 程序窗口一闪而过
**解决方法**: 这是正常现象,说明程序正在初始化。如果持续闪退,请检查是否缺少依赖库。

## 技术支持

如遇到其他问题,请联系指导教师或技术支持人员。

## 文件说明

- `projection_experiment.py`: 主程序源代码
- `requirements.txt`: Python依赖库列表
- `打包程序.bat`: Windows自动打包脚本
- `使用说明.md`: 程序使用说明
