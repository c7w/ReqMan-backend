# Useful interfaces

## Session Uitls

**现在cookie统一变成参数！！！不再查验cookie！！！**
**单测加在cookie里会被自动移动到相应方法参数中**

### uitls.SessionAuthentication
完成ViewSet的用户sessionId验证

下面给出一个写接口的示例
```python
from rest_framework import viewsets
from utils.sessions import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response


class UserViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication]

    @action(detail=False, methods=['POST'])
    def check_username_available(self, req: Request):
        return Response({
            'code': 0
        })
```
如果用户的cookie中没有`sessionId`，将会`exceptions.AuthenticationFailed`。视图函数将不会被调用

视图函数无需处理`sessionId`

后续的视图函数 `request.user` 为
- None，如果没有登录
- User Instance，如果已经登录

后续的视图函数 `request.auth` 为
- SessionId，不过你在视图中将不会用到它

### ums.utils
详见相关函数注释
