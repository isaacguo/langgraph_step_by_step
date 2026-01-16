# Project 10: LangGraph Demo System

## 概述
这是一个综合性的 LangGraph 演示系统，展示了 LangGraph 的核心功能和实际应用场景。系统实现了一个智能任务处理工作流，能够自动分类任务、路由到相应的处理节点、并行处理、错误处理，并最终汇总结果。

## 系统架构

### 核心功能
1. **任务分类** - 自动分析任务类型（研究、计算、写作、分析、复杂任务）
2. **条件路由** - 根据任务类型智能路由到相应的处理节点
3. **并行处理** - 支持多个任务并行执行
4. **结果汇总** - 自动聚合所有处理结果
5. **错误处理** - 完善的错误处理和恢复机制
6. **状态管理** - 完整的状态跟踪和管理

### 工作流程

```
输入任务
    ↓
任务分类节点
    ↓
条件路由
    ↓
┌─────┬─────┬─────┬─────┬─────────┐
│研究 │计算 │写作 │分析 │复杂任务 │
└─────┴─────┴─────┴─────┴─────────┘
    ↓
并行处理（如需要）
    ↓
结果合并
    ↓
结果汇总
    ↓
最终输出
```

## 节点说明

### 1. 分类节点 (classify)
- 分析任务内容
- 确定任务类型
- 为后续路由提供依据

### 2. 处理节点
- **研究节点 (research)**: 处理研究类任务，提供详细的研究结果
- **计算节点 (calculation)**: 处理数学计算类任务
- **写作节点 (writing)**: 处理内容创作类任务
- **分析节点 (analysis)**: 处理数据分析类任务
- **复杂任务节点 (complex)**: 处理需要多步骤的复杂任务

### 3. 并行处理节点
- **parallel_research_1**: 并行研究节点 1
- **parallel_research_2**: 并行研究节点 2
- **merge_parallel**: 合并并行结果

### 4. 汇总节点 (aggregate)
- 收集所有处理结果
- 生成最终输出

### 5. 错误处理节点 (error_handler)
- 捕获和处理错误
- 提供错误恢复机制

## 状态管理

系统使用 `TaskState` 来管理整个工作流的状态：

```python
class TaskState(TypedDict):
    task: str                    # 原始任务
    task_type: str              # 任务类型
    messages: list              # 消息历史
    research_result: str        # 研究结果
    calculation_result: str     # 计算结果
    writing_result: str         # 写作结果
    analysis_result: str        # 分析结果
    parallel_results: list      # 并行处理结果
    final_result: str           # 最终结果
    step_count: int             # 执行步骤计数
    error: str                  # 错误信息
    status: str                 # 当前状态
```

## 运行示例

### 前置要求
1. 确保已安装所有依赖（见 requirements.txt）
2. LM Studio 正在运行，模型 `qwen/qwen3-4b-2507` 已加载
3. LM Studio 服务器在端口 1234 上运行

### 运行步骤

```bash
# 激活 conda 环境
conda activate langgraph_exec

# 进入项目目录
cd project_10_langgraph_demo

# 运行演示系统
python 01_demo_system.py
```

### 示例输出
系统会运行多个示例任务，展示不同类型任务的处理流程：
1. 研究任务示例
2. 计算任务示例
3. 写作任务示例
4. 分析任务示例
5. 复杂/并行任务示例

### 交互式模式
取消注释代码中的 `interactive_demo()` 调用，可以进入交互式模式，实时输入任务进行处理。

## LangGraph 特性展示

### 1. 状态图 (StateGraph)
- 使用 TypedDict 定义强类型状态
- 状态在节点间自动传递和合并

### 2. 条件路由 (Conditional Edges)
- 基于状态动态决定下一步执行路径
- 支持复杂的路由逻辑

### 3. 并行执行
- 使用 `operator.add` 实现并行节点的结果合并
- 展示 fan-out/fan-in 模式

### 4. 节点组合
- 模块化的节点设计
- 易于扩展和维护

### 5. 错误处理
- 条件路由到错误处理节点
- 优雅的错误恢复

## 扩展建议

1. **添加更多节点类型**
   - 图像处理节点
   - 数据查询节点
   - API 调用节点

2. **增强并行处理**
   - 支持更多并行节点
   - 动态并行度调整

3. **持久化状态**
   - 使用 checkpointer 保存状态
   - 支持工作流恢复

4. **可视化**
   - 使用 `app.get_graph().draw_mermaid()` 生成流程图
   - 实时状态监控

5. **性能优化**
   - 缓存机制
   - 批量处理

## 学习要点

通过这个演示系统，你可以学习到：

1. **如何设计 LangGraph 工作流**
   - 状态模式设计
   - 节点职责划分
   - 路由逻辑设计

2. **条件路由的使用**
   - 何时使用条件路由
   - 如何设计路由函数
   - 路由映射配置

3. **并行处理模式**
   - fan-out/fan-in 模式
   - 结果合并策略
   - 状态同步

4. **错误处理策略**
   - 错误检测
   - 错误恢复
   - 优雅降级

5. **实际应用场景**
   - 任务处理系统
   - 智能路由系统
   - 多步骤工作流

## 相关资源

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [LangGraph 教程](https://langchain-ai.github.io/langgraph/tutorials/)
- [状态管理最佳实践](https://langchain-ai.github.io/langgraph/how-tos/state/)
