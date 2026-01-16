#!/bin/bash
echo "=== Prometheus 诊断脚本 ==="
echo ""

echo "1. 检查应用 Pod 状态:"
kubectl get pods -n langgraph-safety -l app=langgraph-app
echo ""

echo "2. 检查 Prometheus Pod 状态:"
kubectl get pods -n langgraph-safety -l app=prometheus
echo ""

echo "3. 测试应用 metrics 端点:"
POD_NAME=$(kubectl get pods -n langgraph-safety -l app=langgraph-app -o jsonpath='{.items[0].metadata.name}')
if [ -n "$POD_NAME" ]; then
    echo "Pod: $POD_NAME"
    kubectl exec -n langgraph-safety $POD_NAME -- curl -s http://localhost:8000/metrics | head -20
else
    echo "未找到应用 Pod"
fi
echo ""

echo "4. 检查 Prometheus targets:"
PROM_POD=$(kubectl get pods -n langgraph-safety -l app=prometheus -o jsonpath='{.items[0].metadata.name}')
if [ -n "$PROM_POD" ]; then
    echo "Prometheus Pod: $PROM_POD"
    echo "访问 http://localhost:30001/targets 查看抓取状态"
    echo "或运行: kubectl port-forward svc/prometheus-service 9090:9090 -n langgraph-safety"
else
    echo "未找到 Prometheus Pod"
fi
echo ""

echo "5. 发送测试请求生成指标:"
echo "运行以下命令发送测试请求:"
echo "curl -X POST http://localhost:30000/chat -H 'Content-Type: application/json' -d '{\"user_id\":\"test\",\"content\":\"hello\"}'"
echo ""

echo "6. 在 Prometheus 中查询所有指标:"
echo "运行查询: {__name__=~\"safety_.*\"}"
