# Grafana 监控指南

## 访问 Grafana

### 方式 1: NodePort（推荐）
```bash
open http://localhost:30002
```

### 方式 2: Port Forward
```bash
kubectl port-forward svc/grafana-service 3000:3000 -n langgraph-safety
open http://localhost:3000
```

## 登录信息

- **用户名**: `admin`
- **密码**: `admin`

首次登录后，系统会提示修改密码（可选）。

## 预配置内容

### 1. Prometheus 数据源
已自动配置 Prometheus 数据源，指向 `http://prometheus-service:9090`

### 2. 预置仪表板
已自动加载 "LangGraph Safety System" 仪表板，包含以下面板：

- **Request Rate**: 显示请求速率（按状态分类）
- **Violation Rate**: 显示违规速率（按类型分类）
- **Average Latency**: 显示平均延迟（Gauge）
- **Safety Score**: 显示当前安全评分（Gauge，0-1范围）

## 查看仪表板

1. 登录后，点击左侧菜单的 **Dashboards** (四个方块图标)
2. 选择 **LangGraph Safety System**
3. 仪表板会自动刷新（每10秒）

## 查询指标

在 Grafana 中，你可以使用 PromQL 查询：

### 常用查询

```promql
# 总请求数
safety_requests_total

# 请求速率
rate(safety_requests_total[5m])

# 违规总数
safety_violations_total

# 违规速率
rate(safety_violations_total[5m])

# 平均延迟
rate(safety_validation_latency_seconds_sum[5m]) / rate(safety_validation_latency_seconds_count[5m])

# 当前安全评分
safety_score_current
```

## 创建自定义仪表板

1. 点击 **+** → **Create Dashboard**
2. 点击 **Add visualization**
3. 选择 **Prometheus** 数据源
4. 输入 PromQL 查询
5. 配置可视化选项

## 故障排查

### Grafana 无法访问
```bash
# 检查 Pod 状态
kubectl get pods -n langgraph-safety -l app=grafana

# 查看日志
kubectl logs -n langgraph-safety -l app=grafana
```

### 数据源连接失败
```bash
# 检查 Prometheus 服务
kubectl get svc -n langgraph-safety prometheus-service

# 测试连接
kubectl exec -n langgraph-safety deployment/grafana -- wget -qO- http://prometheus-service:9090/api/v1/status/config
```

### 仪表板没有数据
1. 确认 Prometheus 正在抓取指标（访问 http://localhost:30001/targets）
2. 发送一些测试请求生成指标：
   ```bash
   curl -X POST http://localhost:30000/chat \
     -H "Content-Type: application/json" \
     -d '{"user_id":"test","content":"hello"}'
   ```
3. 等待 15-30 秒让 Prometheus 抓取数据
4. 在 Grafana 中刷新仪表板
