# undefined 后端项目

## For Users

请查看 `config.yml.bak` 中的说明。

```yaml
# You should finish this file and move it to `./config/config.yml` to deploy your own site.
site:
    debug: false
    secret_key: "django-insecure-vyuaosduoiasbduiasdbiuasobdisaoBULABULA"
    allowed_hosts: # CORS
    - 'https://undefined.c7w.tech'
    - 'https://frontend-undefined.app.secoder.net'
    - '*'

database:
    type: "mysql" # Choose between "mysql" and "sqlite3", the latter would lose data after updating
    host: "mysql.undefined.secoder.local"
    port: 3306
    name: "PROJECT_DATABASE"
    user: "YOUR_USER"
    password: "THERE_SHOULD_BE_A_PASSWORD"
```

## For Developers

请先阅读[项目规范](https://qynt1gy8vn.feishu.cn/docs/doccnLXFY9wOriyviGh5fv6NUgd)，然后再继续阅读本部分。

为了通过 CI 请在 push 之前自行运行脚本 `./test.sh`，会自动执行风格测试与单元测试。

为了代码风格统一，我们安装了 black 库：

+ https://zhuanlan.zhihu.com/p/203307235

也就是说，你只需要在补全依赖之后，使用 `black <你的模块名>` 即可自动 format。

请注意一次 commit 不能过 500 行的限制。

## 数据库模型

### UMS

#### User

+ id: BigAuto, primary_key
+ name: Text, indexed, 不允许重复
+ password: Text (sha256)
+ email: Text, indexed
+ avatar: Text (base64)
+ disabled: Boolean
+ createdAt: Float

#### SessionPool

+ sessionId: Text, indexed
+ user: FK
+ expiredAt: datetime (AUTO DELETE AFTER expiration)

#### Project

+ id: BigAuto, primary_key
+ title: Text, indexed
+ description: Text, indexed (Markdown)
+ invitation: Text
+ disabled: Boolean
+ createdAt: Float

#### UserProjectAssociation

+ user: ForeignKey, indexed
+ project: ForeignKey, indexed
+ role: Text (enum "member", "dev", "qa", "sys", "supermaster")

// User + Project 联合唯一

#### ProjectInvitationAssociation

+ project: FK, ind
+ invitation: Text, ind（邀请码，用户注册使用直接加身份）
+ role: Text (enum role)

### RMS

#### Iteration

+ id: BigAuto, primary_key
+ project: ForeignKey, indexed
+ sid: Integer, 在项目中的 id
+ title: Text, 显示名
+ begin: Float
+ end: Float
+ disabled: Boolean
+ createdAt: Float

#### UserIterationAssociation

+ user: ForeignKey, indexed
+ iteration: ForeignKey, indexed

// user + iteration 联合唯一，代表 iteration 由用户主管

#### IR

+ id: BigAuto, pk
+ project: ForeignKey, indexed
+ title: Text, 显示名，要求与 project 联合唯一, indexed
+ description: Text (markdown)
+ rank: Integer // 同一个项目内，IR 按照 rank 顺序升序展示
+ createdBy: FK
+ createdAt: float
+ disabled: Boolean

#### SR

+ id: BA, pk
+ project: FK, indexed
+ title: 同上, indexed
+ description: 同上
+ priority: Integer // 开发工作中这一件事的重要性，方便进行完成进度统计
+ rank: Integer // 同一个 IR 内，SR 按照 rank 顺序升序展示
+ state: enum("TODO", "WIP", "Reviewing", "Done")
+ createdBy: FK
+ createdAt: float
+ disabled: Boolean

#### IRSRAssociation

出于一个 SR 可能解决多个 IR，一个 IR 可能对应多个 SR 的考虑，建立多对多联系。

+ IR: FK
+ SR: FK

#### SRIterationAssociation

+ SR: FK
+ iteration: FK

#### Service

+ id: BigAuto, pk
+ project: ForeignKey, indexed
+ title: Text, 显示名，要求与 project 联合唯一, indexed
+ description: Text (markdown)
+ rank: Integer // 同一个项目内，Service 按照 rank 顺序升序展示
+ createdBy: FK
+ createdAt: FK
+ disabled: Boolean

#### SR_Changelog

+ id: BigAuto, PK
+ project: FK
+ SR: FK
+ description: Text (Why It was changed?)
+ formerState: enum
+ formerDescription: Text
+ changedBy: FK
+ changedAt: float

### RDTS

#### Repository

+ id: BigAuto, pk
+ url: string
+ project: ForeignKey
+ title: Text, 显示名，要求与 project 联合唯一, indexed
+ description: Text (markdown)
+ createdBy: FK
+ createdAt: FK
+ disabled: Boolean

#### Commit

+ id: BigAuto, pk
+ hash_id: string
+ repo: FK
+ title: Text
+ message: Text
+ commiter_email:string
+ createdAt: float
+ disabled: Boolean

照着这个建：

+ https://gitlab.secoder.net/api/v4/projects/468/repository/commits

```json
{"id":"d6ba051d2b107287ee7a036e7defcadeb151e538","short_id":"d6ba051d","created_at":"2022-03-15T20:32:32.000+08:00","parent_ids":["4afe7fb64ef32997c5ee72465b09f4239bed8bea"],"title":"[SR.001.000] Fix routing issues: remove .htaccess, modify nginx settings","message":"[SR.001.000] Fix routing issues: remove .htaccess, modify nginx settings\n","author_name":"c7w","author_email":"admin@cc7w.cf","authored_date":"2022-03-15T20:32:32.000+08:00","committer_name":"c7w","committer_email":"admin@cc7w.cf","committed_date":"2022-03-15T20:32:32.000+08:00","web_url":"https://gitlab.secoder.net/undefined/frontend/-/commit/d6ba051d2b107287ee7a036e7defcadeb151e538"}
```

#### Merge Request

+ id: BigAuto, pk
+ merge_id: Integer
+ repo: FK
+ title: Text
+ description:text
+ state: enum
+ authoredByEmail: string,allow_null
+ authoredAt: float, allow_null
+ reviewedByEmail: string, allow_null
+ reviewedAt: float, allow_null
+ disabled: Boolean

照着这个建：

+ https://gitlab.secoder.net/api/v4/projects/468/merge_requests

```json
{"id":60,"iid":8,"project_id":468,"title":"[SR.001.002.F] Modify SonarQube properties","description":"[SR.001.002] Modify SonarQube properties","state":"merged","created_at":"2022-03-15T06:36:09.461Z","updated_at":"2022-03-15T06:45:56.029Z","merged_by":{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"},"merged_at":"2022-03-15T06:45:26.204Z","closed_by":null,"closed_at":null,"target_branch":"dev","source_branch":"feature-001-002","user_notes_count":0,"upvotes":0,"downvotes":0,"author":{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"},"assignees":[],"assignee":null,"source_project_id":468,"target_project_id":468,"labels":["infrastructure"],"work_in_progress":false,"milestone":null,"merge_when_pipeline_succeeds":false,"merge_status":"cannot_be_merged","sha":"0d4457764c1d034a8438f7e344de047d2f13b675","merge_commit_sha":"35c111aaa4f153f67aeb931d36d55c2a07ae0e85","squash_commit_sha":null,"discussion_locked":null,"should_remove_source_branch":null,"force_remove_source_branch":true,"reference":"!8","references":{"short":"!8","relative":"!8","full":"undefined/frontend!8"},"web_url":"https://gitlab.secoder.net/undefined/frontend/-/merge_requests/8","time_stats":{"time_estimate":0,"total_time_spent":0,"human_time_estimate":null,"human_total_time_spent":null},"squash":false,"task_completion_status":{"count":0,"completed_count":0},"has_conflicts":true,"blocking_discussions_resolved":true}
```



#### Issue

// 这里的 issue 不指议题，单指缺陷

+ id: BigAuto, pk
+ issue_id: Integer
+ repo: FK
+ title: Text
+ description:text
+ state: enum
+ authoredByEmail: text, allow_null
+ authoredAt: float, allow_null
+ reviewedByEmail: text, allow_null
+ reviewedAt: float, allow_null
+ disabled: Boolean

朝着这个建：

+ https://gitlab.secoder.net/api/v4/projects/468/issues

```json
{"id":167,"iid":8,"project_id":468,"title":"[SR.002.001] 增加前端部署用分支配置文件","description":"[SR.002.001] 增加前端部署用分支配置文件\n并完成 readme.md 中的有关说明","state":"opened","created_at":"2022-03-15T06:04:34.022Z","updated_at":"2022-03-15T06:04:34.022Z","closed_at":null,"closed_by":null,"labels":["infrastructure"],"milestone":null,"assignees":[{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"}],"author":{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"},"assignee":{"id":122,"name":"高焕昂","username":"2020010951","state":"active","avatar_url":"https://gitlab.secoder.net/uploads/-/system/user/avatar/122/avatar.png","web_url":"https://gitlab.secoder.net/2020010951"},"user_notes_count":0,"merge_requests_count":0,"upvotes":0,"downvotes":0,"due_date":"2022-03-22","confidential":false,"discussion_locked":null,"web_url":"https://gitlab.secoder.net/undefined/frontend/-/issues/8","time_stats":{"time_estimate":0,"total_time_spent":0,"human_time_estimate":null,"human_total_time_spent":null},"task_completion_status":{"count":0,"completed_count":0},"has_tasks":false,"_links":{"self":"https://gitlab.secoder.net/api/v4/projects/468/issues/8","notes":"https://gitlab.secoder.net/api/v4/projects/468/issues/8/notes","award_emoji":"https://gitlab.secoder.net/api/v4/projects/468/issues/8/award_emoji","project":"https://gitlab.secoder.net/api/v4/projects/468"},"references":{"short":"#8","relative":"#8","full":"undefined/frontend#8"},"moved_to_id":null}
```

#### CommitSRAssociation

+ commit: FK
+ SR: FK

#### MRSRAssociation

+ MR: FK
+ SR: FK

#### IssueSRAssociation

+ issue: FK
+ SR: FK

## 仓库访问令牌与 GitLab API

Repo > 设置 > 访问令牌

+ frontend: SxG2cW1sHs2vtZLdQxv4

## API

> **API 的外部呈现**
>
> 使用 类 Swagger 风格的生成器
>
> + https://github.com/axnsan12/drf-yasg/

若不加说明，[GET/POST] 方法的 [请求参数/请求体] 中均带有 sessionId 字段用于鉴权。

### 鉴权注意
当前使用的鉴权机制
+ 首先判断是否有sessionId，没有的，`AuthenticationFailed`， -4
+ 再判断有无权限访问，比如只有supermaster能修改项目信息等， 权限不足， `PermissionDenied`, -2
+ 再判断用户访问是否过于频繁，过于频繁，`Throttled`，-3
+ 再判断请求是否缺乏必要的参数，缺乏的， `ParamErr`, -1
+ 做完了这些，控制权被移交给相应API函数，API函数也可能发出上述异常
+ 意料之外的Exception, -100


### `/ums/`

**所有请求都需要在cookie中包含sessionId，否则一律403 Forbidden** 

#### `[GET] /ums/user/`

Request params:

+ sessionId: str

Response:

+ code: 0 if success, 1 if not logged in
+ data
  + user: model_to_dict(User)
  + projects: filter and model_to_dict(Project)
  + schedule
    + done: {}
    + wip: {}
    + todo: {}

#### `[POST] /ums/login/`

Request Body:

- sessionId: str
- identity: str (username or email)
- password: str (already after md5, sha256 it and check)

Response:

+ code: 0 if success, 1 if already logged in, 2 if invalid identity, 3 if invalid password

#### `[POST] /ums/logout/`

Request Body:

+ sessionId: str

Response:

+ code: 0 if success, 1 if not logged in

#### `[POST] /ums/register/`

Request Body:

+ sessionId: str
+ name: str 
+ password: str (already after md5, sha256 it and check)
+ email: str (Remember to check if contains '@')
+ invitation: [Optional] str

Response:

+ code: 0 if success, 2 invalid invitation, 1 otherwise

#### `[POST] /ums/check_username_available/`

+ name: str

Response:

+ code: 0 if available, 1 otherwise

Explanation:

+ 这里 available 是说没有被占用，用户可以使用这个来注册

#### `[POST] /ums/check_email_available/`

+ email: str

Response:

+ code: 0 if available, 1 otherwise

#### `[POST] /ums/modify_user_role/`

+ project: int, project_id
+ user: int, user_id, user to be modified
+ role: str, the name of the new role, using (member, dev, qa, sys, supermaster)

Response:

+ code 0 if successful, 1 otherwise

#### `[POST] /ums/project_rm_user/`

+ project: int, project_id
+ user: int, user_id, user to be removed

Response:

+ code 0 if successful, 1 otherwise

#### `[POST] /ums/project_add_user/`

+ project: int, project_id
+ user: int, user_id, user to be added
+ role: str, the name of the new role, using (member, dev, qa, sys, supermaster)

Response:

+ code 0 if successful, 1 otherwise

#### `[POST] /ums/project/`

+ project: id of the project

Response:

+ code: 0 if successful, 1 otherwise
+ data: 
    + project: proj_to_list
    + users: filter and user_to_list

#### `[POST] /ums/modify_project/`

+ id
+ title
+ description

Response

+ code 0 if successful else 1

#### `[POST] /ums/refresh_invitation/`

+ project

Response

+ code 0 if successful else 1
+ data 
    + invitation

#### `[POST] /ums/get_invitation/`

+ project

Response

+ code 0 if successful else 1
+ data 
    + invitation



### `/rms/`

+ 获取用户参与的所有项目
+ 用户输入邀请码加入项目，成为开发工程师
+ 用户新建项目，成为系统工程师

#### 统一接口
+ 这里留一个**统一的接口**，`[GET|POST] /rms/project/`
  + 给定某个项目ID，[READ/CREATE/UPDATE/DELETE, 以下简称 CRUD] IR
  + 给定某个项目ID，CRUD 所有的 SR
  + 给定某个项目ID，CRUD 所有的 Iteration
  + 给定某个项目ID，CRD IR-SR // A-B 代表两者之间的联系
  + 给定某个项目ID，CRD 的 SR-Iteration
  + 给定某个项目ID，CRUD Service
  + 给定某个项目ID，CRD User-Iteration
+ 

#### `[GET] /rms/project/`

+ project (id)
+ type (sr,ir,iteration,ir-sr,sr-iteration,service,user-iteration)


Response

+ code: 0 if success, 1 if not log in
+ data: list of data

Explanation

+ 这里的 list 是对应种类数据的 List, 每个是一个对象

#### `[POST] /rms/project/`

+ project (id)

+ type (sr,ir,iteration,ir-sr,sr-iteration,service,user-iteration) (string)

+ operation (update,create,delete) (string)

+ data:

```python
  "data" :{ # update
  	id:
  	updateData:{
  		'title':'TitleText'
  	}
  }
  
  "data" :{ # delete ir sr iteration service
      id:
  }
  
  "data":{ # delete relation
      iterationId:
      IRId:
      SRId:
  }
  
  "data" :{ # create
      updateData:{
          'title':....,
          ...
          IRId SRId iterationId:
          userId
      }
  }
```

  

Response
+ code 0 if success, else 1

Explanation
+ 创建操作需要提交的数据参数参考前面的数据库设计
+ 部分种类数据无法 update 参考请求上方统一接口定义

### `/rdts/`

这里留一个**统一的接口**， `[GET|POST] /rdts/project/`

+ 给定某个项目ID
+ CRUD 所有的 Repo, Commit, MR
+ CRD 三种 Association

#### `[GET] /rdts/project/`

* project (id)
* type (repo)

other types

* repo (id)
* type (commit,mr,issue,commit-sr,mr-sr,issue-sr)

Response:

* code 0 if success
* data: list of data

#### `[POST] /rdts/project/`

* project (id)

* type (repo,commit,mr,issue,commit-sr,mr-sr,issue-sr)

* operation (update,create,delete)

* data：

  ```python
    "data" :{ # update
    	id:
    	updateData:{
    		'title':'TitleText'
    	}
    }
    
    "data" :{ # delete repo commit mr issue
        id:
    }
    
    "data":{ # delete relation
        MRId:
        commitId:
        SRId:
        issueId:
    }
    
    "data" :{ # create
        updateData:{
            'title':....,
            ...
            MRId SRId issueId:
            commitId
        }
    }
  ```

  

## Crontab

本项目需要定时任务拉取远端仓库的信息。

+ 在 Header 中添加 "PRIVATE-TOKEN: <your_access_token>" 
+ 访问 Repo 记录的对应 URL（如上 RDTS 部分记录的三个 URL）

我们需要以下定时任务：

+ 定时拉取最新的 Commit
+ 定时拉取最新的 PR
+ 定时拉取最新的 Issue

同时将数据库中的相应数据字段同步。



自动关联功能：

+ 定义相应的正则匹配表达式，当自动拉取的三种消息匹配到相应的正则表达式，便自动与 SR 的状态相关联。
