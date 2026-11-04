# DWG 瘦身助手

免登录、免安装的 DWG 审计与重新写入网页服务，面向 Render Docker 部署。

## 隐私

- 上传文件仅保存在系统临时目录。
- 响应完成后自动删除输入与输出文件。
- 不使用数据库，不记录图纸内容。

## 引擎许可

转换由 ODA File Converter 完成。部署者必须自行确认并遵守 Open Design Alliance 的许可条款；当前免费下载页面标注 60 天试用。本项目本身不重新分发 ODA 二进制文件，容器构建时从 ODA 官方地址下载。

## 本地运行

```bash
docker build -t dwg-slim-web .
docker run --rm -p 10000:10000 dwg-slim-web
```
